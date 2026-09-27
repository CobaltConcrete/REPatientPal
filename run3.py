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
        "Read the visible text in this medical document. Return a faithful transcription, "
        "a short plain-language summary, and a translation of that summary into "
        f"{language_name}. Preserve names, dates, numbers, medication names, and uncertainty. "
        "Do not diagnose, add facts, or recommend treatment. If text is unreadable, say so. "
        "This is language assistance, not medical advice. Return only JSON with string keys "
        "source_text, summary, and translation."
    )
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json", max_output_tokens=2048),
        )
        data = json.loads(response.text or "")
        result = {key: str(data.get(key, "")).strip() for key in ("source_text", "summary", "translation")}
        if not all(result.values()):
            raise ValueError("The model returned an incomplete report.")
        return result
    except Exception as exc:
        raise ProcessingError("The document could not be processed. Please try again later.") from exc
    finally:
        client.close()


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
