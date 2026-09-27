"""Stateless image-to-summary pipeline used by the Flask web app."""

import io
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS
from PIL import Image, UnidentifiedImageError

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
LANGUAGES = {
    "english": ("English", "en"),
    "chinese": ("Simplified Chinese", "zh-CN"),
    "cantonese": ("Cantonese", "yue"),
    "hindi": ("Hindi", "hi"),
}
ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class ProcessingError(Exception):
    """An upstream service failed or returned an unusable result."""


def validate_image(image_bytes):
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image_format = image.format
            if image.width * image.height > 25_000_000:
                raise ValueError("Image dimensions are too large. Choose an image under 25 megapixels.")
            image.verify()
    except ValueError as exc:
        if str(exc).startswith("Image dimensions are too large"):
            raise
        raise ValueError("Upload a valid PNG, JPEG, or WebP image.") from exc
    except Image.DecompressionBombError as exc:
        raise ValueError("Image dimensions are too large. Choose an image under 25 megapixels.") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Upload a valid PNG, JPEG, or WebP image.") from exc

    if image_format not in ALLOWED_FORMATS:
        raise ValueError("Upload a PNG, JPEG, or WebP image.")
    return ALLOWED_FORMATS[image_format]


def _generate_report(image_bytes, mime_type, language_name):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ProcessingError("The Gemini API key is not configured on the server.")

    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=90_000))
    prompt = (
        "Read the visible text in this medical document. Return a faithful transcription "
        "and a plain-language summary in structured blocks, then translate those same "
        f"blocks into {language_name}. Preserve the input's section order and visual "
        "structure: use heading blocks for section headings, paragraph blocks for each "
        "separate paragraph, and bullet or numbered blocks for lists. Do not merge separate "
        "paragraphs or list items into one paragraph. Keep every summary block aligned to "
        "the corresponding translated block, with the same block type and order. Explain "
        "medical terms in simple wording when possible, without changing their meaning. "
        "Keep generic medicine names exactly as written in English in both languages. "
        "Identify medical and medicine terms that appear in both summaries for the glossary; "
        "include their exact English spelling. Preserve uncertainty, and do not invent facts, "
        "diagnose, or recommend treatment. Omit personal identifiers and contact details "
        "from the summary. If text is unreadable, say so. This is language assistance, not "
        "medical advice. Return only JSON matching this shape: {"
        '"source_text": string, '
        '"summary_blocks": [{"type":"heading|paragraph|bullets|numbered", '
        '"text":"...", "items":["..."]}], '
        '"translation_blocks": [{"type":"heading|paragraph|bullets|numbered", '
        '"text":"...", "items":["..."]}], '
        '"glossary_terms": ["English medical or medicine term", ...]}. '
        "For heading/paragraph blocks use text; for bullets/numbered blocks use items."
    )
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json", max_output_tokens=4096),
        )
        data = json.loads(response.text or "")
        summary_blocks = _normalize_blocks(data.get("summary_blocks"))
        translation_blocks = _normalize_blocks(data.get("translation_blocks"))
        if not summary_blocks or len(summary_blocks) != len(translation_blocks):
            raise ValueError("The model returned unaligned report sections.")
        if any(a["type"] != b["type"] for a, b in zip(summary_blocks, translation_blocks)):
            raise ValueError("The model returned mismatched report formatting.")
        raw_terms = data.get("glossary_terms", [])
        if not isinstance(raw_terms, list):
            raw_terms = []
        glossary_terms = list(dict.fromkeys(
            term.strip() for term in raw_terms
            if isinstance(term, str) and term.strip() and len(term.strip()) <= 100
        ))[:30]
        result = {
            "source_text": str(data.get("source_text", "")).strip(),
            "summary": _blocks_to_text(summary_blocks),
            "translation": _blocks_to_text(translation_blocks),
            "summary_blocks": summary_blocks,
            "translation_blocks": translation_blocks,
            "glossary_terms": glossary_terms,
        }
        if not result["source_text"] or not result["summary"] or not result["translation"]:
            raise ValueError("The model returned an incomplete report.")
        return result
    except Exception as exc:
        raise ProcessingError("The document could not be processed. Please try again later.") from exc
    finally:
        client.close()


def _normalize_blocks(raw_blocks):
    if not isinstance(raw_blocks, list):
        return []
    blocks = []
    valid_types = {"heading", "paragraph", "bullets", "numbered"}
    for raw in raw_blocks[:80]:
        if not isinstance(raw, dict) or raw.get("type") not in valid_types:
            continue
        block_type = raw["type"]
        if block_type in {"bullets", "numbered"}:
            items = raw.get("items")
            if not isinstance(items, list):
                continue
            items = [str(item).strip() for item in items if str(item).strip()][:50]
            if items:
                blocks.append({"type": block_type, "items": items})
        else:
            text = str(raw.get("text", "")).strip()
            if text:
                blocks.append({"type": block_type, "text": text})
    return blocks


def _blocks_to_text(blocks):
    rendered = []
    for block in blocks:
        if block["type"] in {"bullets", "numbered"}:
            marker = "- " if block["type"] == "bullets" else "1. "
            rendered.extend(marker + item for item in block["items"])
        else:
            rendered.append(block["text"])
    return "\n\n".join(rendered)


def _synthesize_speech(text, language_code):
    audio = io.BytesIO()
    try:
        gTTS(text=text, lang=language_code, slow=False, timeout=(3, 8)).write_to_fp(audio)
    except Exception as exc:
        raise ProcessingError("Speech generation failed. You can still read the translated text.") from exc
    return audio.getvalue()


def main(image_bytes, language):
    if language not in LANGUAGES:
        raise ValueError("Choose a supported language.")
    mime_type = validate_image(image_bytes)
    language_name, speech_language = LANGUAGES[language]
    report = _generate_report(image_bytes, mime_type, language_name)
    try:
        audio_bytes = _synthesize_speech(report["translation"], speech_language)
    except ProcessingError:
        audio_bytes = None
    return report, audio_bytes
