"""FastAPI endpoints for the NightingAIe document processing service."""

import base64
import logging
import os

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from run3 import ProcessingError, main

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "8"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
allowed_frontend_origins = [
    origin.strip().rstrip("/")
    for origin in (
        "https://nightingaie.onrender.com,"
        "https://nightingaie-frontend.onrender.com,"
        + os.getenv("FRONTEND_ORIGIN", "")
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="NightingAIe API",
    description="Read and explain a health document image, translate it, and return speech audio.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_frontend_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(HTTPException)
async def http_error_response(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/")
def index():
    return {"service": "NightingAIe API", "health": "/health", "documentation": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
def upload_file(file: UploadFile | None = File(None), language: str = Form("")):
    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail="Choose an image to upload.")
    if not language:
        raise HTTPException(status_code=400, detail="Choose a language.")

    image_bytes = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image is too large. Maximum size is {MAX_UPLOAD_MB} MB.",
        )

    try:
        report, audio_bytes = main(image_bytes, language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProcessingError as exc:
        logging.exception("Document processing failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logging.exception("Unexpected document processing error")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while processing the document. Please try again.",
        ) from exc

    return {
        "report": report,
        "audio_base64": base64.b64encode(audio_bytes).decode("ascii") if audio_bytes else None,
        "audio_mime_type": "audio/mpeg" if audio_bytes else None,
    }
