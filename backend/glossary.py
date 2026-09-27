"""Look up patient-friendly medical definitions from NLM sources."""

import html
import json
import os
import re
from difflib import SequenceMatcher
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import time

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
RXNORM_SYSTEM = "2.16.840.1.113883.6.88"
LANGUAGES = {
    "english": "English",
    "chinese": "Simplified Chinese",
    "cantonese": "Cantonese written in Traditional Chinese",
    "hindi": "Hindi",
}
_CACHE = {}
_CACHE_TTL_SECONDS = 12 * 60 * 60


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def _plain_text(value):
    parser = _TextExtractor()
    parser.feed(html.unescape(value or ""))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def _brief_drug_definition(text):
    class_match = re.search(
        r"\b[A-Z][A-Za-z-]*(?:\s+[A-Z][A-Za-z-]*)?\s+(?:is in a class of medications called|belongs to a class of medications called|is a type of medication called)\s+[^.]+\.",
        text,
    )
    if class_match:
        selected = [class_match.group(0)]
        rest = text[class_match.end():]
        mechanism = re.search(r"(?:^|\s)([^.!?]*\bworks by\b[^.!?]*[.!?])", rest, re.I)
        if mechanism:
            selected.append(mechanism.group(1).strip())
    else:
        selected = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)[:2]
    return " ".join(selected)[:750].strip()


def _fetch(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NightingAIe/1.0 medical-glossary"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return response.read()


def _rxnorm_id(term):
    url = "https://rxnav.nlm.nih.gov/REST/rxcui.json?" + urllib.parse.urlencode(
        {"name": term, "search": "2"}
    )
    try:
        data = json.loads(_fetch(url))
        ids = data.get("idGroup", {}).get("rxnormId", [])
        return ids[0] if ids else None
    except Exception:
        return None


def _medlineplus_drug(term, language_code):
    rxnorm_id = _rxnorm_id(term)
    searches = []
    if rxnorm_id:
        searches.append({"mainSearchCriteria.v.c": rxnorm_id})
    # MedlinePlus Connect also supports name-only lookups for English drug information.
    if language_code == "en":
        searches.append({})
    for code_params in searches:
        params = {
            "mainSearchCriteria.v.cs": RXNORM_SYSTEM,
            "mainSearchCriteria.v.dn": term,
            "informationRecipient.languageCode.c": language_code,
            "knowledgeResponseType": "application/xml",
            "tool": "NightingAIe",
            **code_params,
        }
        url = "https://connect.medlineplus.gov/service?" + urllib.parse.urlencode(params)
        try:
            root = ET.fromstring(_fetch(url))
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find("atom:entry", ns)
            if entry is None:
                continue
            title = _plain_text(entry.findtext("atom:title", default="", namespaces=ns))
            summary = _plain_text(entry.findtext("atom:summary", default="", namespaces=ns))
            link = entry.find("atom:link", ns)
            href = link.attrib.get("href", "") if link is not None else ""
            if summary and href:
                return {
                    "title": title or term,
                    "definition": _brief_drug_definition(summary),
                    "url": href,
                    "source": "MedlinePlus, U.S. National Library of Medicine",
                    "rxnorm_id": rxnorm_id,
                }
        except Exception:
            continue
    return None


def _medlineplus_topic(term):
    # Search broadly, then require an exact MedlinePlus title or synonym match below.
    params = {"db": "healthTopics", "term": term, "rettype": "brief", "retmax": "10"}
    url = "https://wsearch.nlm.nih.gov/ws/query?" + urllib.parse.urlencode(params)
    try:
        root = ET.fromstring(_fetch(url))
        documents = root.findall(".//document")
        if not documents:
            return None
        # Prefer an exact title so a broad or ambiguous search does not define the wrong term.
        candidates = []
        for document in documents:
            fields = {}
            for node in document.findall("content"):
                name = node.attrib.get("name")
                value = _plain_text(node.text or "")
                fields.setdefault(name, []).append(value)
            candidates.append((document, fields))
        selected = next(
            (item for item in candidates
             if any(term.casefold() == label.casefold() for label in
                    item[1].get("title", []) + item[1].get("altTitle", []))),
            None,
        )
        if selected is None:
            return None
        document, fields = selected
        definition = (next(iter(fields.get("snippet", [])), "")
                      or next(iter(fields.get("FullSummary", [])), "")
                      or next(iter(fields.get("full-summary", [])), ""))
        if not definition:
            return None
        return {
            "title": next(iter(fields.get("title", [])), term),
            "definition": definition[:1800],
            "url": document.attrib.get("url", "https://medlineplus.gov/"),
            "source": "MedlinePlus, U.S. National Library of Medicine",
            "rxnorm_id": None,
        }
    except Exception:
        return None


def _mesh_definition(term):
    lookup_url = "https://id.nlm.nih.gov/mesh/lookup/descriptor?" + urllib.parse.urlencode(
        {"label": term, "match": "contains", "limit": "10"}
    )
    try:
        matches = json.loads(_fetch(lookup_url))
        if isinstance(matches, dict):
            matches = [matches]
        matches = [match for match in matches if match.get("resource") and match.get("label")]
        if not matches:
            return None
        match = max(
            matches,
            key=lambda item: SequenceMatcher(None, term.casefold(), item["label"].casefold()).ratio(),
        )
        descriptor = match["resource"].rsplit("/", 1)[-1]
        record = json.loads(_fetch(f"https://id.nlm.nih.gov/mesh/{descriptor}.json"))
        concept_url = record.get("preferredConcept")
        if not concept_url:
            return None
        concept = json.loads(_fetch(concept_url + ".json"))
        scope_note = concept.get("scopeNote", {}).get("@value", "").strip()
        if not scope_note:
            return None
        return {
            "title": match["label"],
            "definition": scope_note,
            "url": f"https://meshb.nlm.nih.gov/record/ui?ui={descriptor}",
            "source": "Medical Subject Headings (MeSH), U.S. National Library of Medicine",
            "rxnorm_id": None,
        }
    except Exception:
        return None


def _lookup(term):
    key = term.casefold()
    cached = _CACHE.get(key)
    if cached and time.monotonic() - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]
    result = _medlineplus_drug(term, "en")
    if not result:
        topic = _medlineplus_topic(term)
        if topic and topic["title"].casefold() == term.casefold():
            result = topic
        else:
            result = _mesh_definition(term) or topic
    if not result:
        raise LookupError("No trusted glossary entry was found for that term.")
    if len(_CACHE) >= 512:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[key] = (time.monotonic(), result)
    return result


def _dailymed_label(rxnorm_id):
    if not rxnorm_id:
        return None
    url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?" + urllib.parse.urlencode(
        {"rxcui": rxnorm_id, "pagesize": "1"}
    )
    try:
        data = json.loads(_fetch(url)).get("data", [])
        if not data:
            return None
        label = data[0]
        set_id = label.get("setid")
        if not set_id:
            return None
        return {
            "name": "DailyMed official drug label: " + label.get("title", "Drug label"),
            "url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?" + urllib.parse.urlencode({"setid": set_id}),
        }
    except Exception:
        return None


def lookup_glossary(term, language):
    term = " ".join(term.strip().split())
    language = language.lower()
    if not term or len(term) > 100 or language not in LANGUAGES:
        raise ValueError("Enter a valid medical term and supported language.")
    entry = _lookup(term)
    definition = entry["definition"]
    if language == "chinese":
        language_code = "zh"
    elif language == "cantonese":
        language_code = "zh-HK"
    elif language == "hindi":
        language_code = "hi"
    else:
        language_code = "en"

    if language_code != "en":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Glossary translation is unavailable because the server key is not configured.")
        from google import genai

        client = genai.Client(api_key=api_key)
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=(
                    f"Translate this patient-friendly medical definition into {LANGUAGES[language]}. "
                    "Keep the meaning precise, use plain language, do not add information or advice, "
                    "and return only the translation.\n\n" + definition
                ),
            )
            definition = (response.text or "").strip()
            if not definition:
                raise RuntimeError("The glossary translation was empty.")
        finally:
            client.close()

    sources = [{"name": entry["source"], "url": entry["url"]}]
    if entry["rxnorm_id"]:
        sources.append(_dailymed_label(entry["rxnorm_id"]) or {
            "name": "DailyMed, U.S. National Library of Medicine drug labels",
            "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?" + urllib.parse.urlencode({"query": term}),
        })
        sources.append({
            "name": "RxNorm, U.S. National Library of Medicine",
            "url": f"https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm={entry['rxnorm_id']}",
        })
    else:
        if entry["source"].startswith("MedlinePlus"):
            sources.append({
                "name": "Medical Subject Headings (MeSH), U.S. National Library of Medicine",
                "url": "https://meshb.nlm.nih.gov/search?" + urllib.parse.urlencode({"searchTerm": term}),
            })
    return {
        "term": entry["title"],
        "definition": definition,
        "language": language,
        "translated": language_code != "en",
        "sources": sources,
    }
