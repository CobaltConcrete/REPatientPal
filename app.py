from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS  # Import CORS
from run3 import image_to_text, simplify_text, translate_text, text_to_speech, main  # Import your functions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Process the image
    # medical_report = image_to_text(filepath)
    # response_list = simplify_text(medical_report)
    # translated_text = translate_text(response_list)
    # speech = text_to_speech(translated_text)

    # Save the audio file
    audio_file_path = 'C:\Save Data Here\Coding stuff\Projects\REPatientPal\output.mp3'
    # speech.save(audio_file_path)

    translated_text, audio_base64 = main(filepath)
    print(audio_base64)

    return jsonify({
        "text": translated_text,
        "audiobase64": audio_base64
    })

@app.route('/audio/<filename>', methods=['GET'])
def get_audio(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
