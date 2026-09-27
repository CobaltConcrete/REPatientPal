import base64
import logging
import os

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from run3 import ProcessingError, main

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024
allowed_frontend_origins = {
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_ORIGIN", "").split(",")
    if origin.strip()
}


@app.after_request
def add_frontend_cors_headers(response):
    origin = request.headers.get("Origin", "").rstrip("/")
    if origin and origin in allowed_frontend_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers.add("Vary", "Origin")
    return response


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/upload")
def upload_file():
    image = request.files.get("file")
    language = request.form.get("language", "")
    if image is None:
        return jsonify(error="Choose an image to upload."), 400
    if not image.filename:
        return jsonify(error="Choose an image to upload."), 400
    if not language:
        return jsonify(error="Choose a language."), 400

    try:
        report, audio_bytes = main(image.read(), language)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except ProcessingError as exc:
        logging.exception("Document processing failed")
        return jsonify(error=str(exc)), 502
    except Exception:
        logging.exception("Unexpected document processing error")
        return jsonify(error="Something went wrong while processing the document. Please try again."), 500

    return jsonify(
        report=report,
        audio_base64=base64.b64encode(audio_bytes).decode("ascii") if audio_bytes else None,
        audio_mime_type="audio/mpeg" if audio_bytes else None,
    )


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    return jsonify(error=f"Image is too large. Maximum size is {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)} MB."), 413


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
