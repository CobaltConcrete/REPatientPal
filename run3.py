import os
import requests
import google.generativeai as genai
import translators as ts
from gtts import gTTS
import base64

API_KEY = "AIzaSyAfBEPXr9mrGbMWbb5YkwigTIH_nv2hQ58"

languages = {
    "english": ["en", "en"]
    "chinese": ["zh", "zh"]
    "cantonese": ["zh-yue", yue]
}

def image_to_text(image_path):
    api_url = 'https://api.api-ninjas.com/v1/imagetotext'
    image_file_descriptor = open(image_path, 'rb')
    files = {'image': image_file_descriptor}
    r = requests.post(api_url, files=files)
    # print(r.json())
    medical_report = r.json()
    return medical_report

def simplify_text(medical_report):
    # Access your API key as an environment variable.
    genai.configure(api_key=API_KEY)
    # Choose a model that's appropriate for your use case.
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"Simplify this medical report for me, highlighting the important medical jargon. {medical_report}"

    response = model.generate_content(prompt)

    response_text = response.text
    response_list = response_text.split("\n")

    for line in response_list:
        print(line)

    return response_list

def translate_text(response_list):
    chinese_text = ""

    ## Translators as ts
    for line in response_list:
        translated_line = ts.translate_text(query_text = line, translator = 'bing', from_language = 'en', to_language = 'zh-yue')
        print(translated_line)
        cleaned_translated_line = translated_line.replace("*", "")
        chinese_text += cleaned_translated_line
        chinese_text += "\n"
    
    return chinese_text

def text_to_speech(chinese_text):
    audio_file_path = "C:\Save Data Here\Coding stuff\Projects\REPatientPal\outputwebsite.mp3"

    # Language in which you want to convert
    language = "yue"

    # Creating an object for gTTS
    speech = gTTS(text=chinese_text, lang=language)

    # Saving the converted audio in a mp3 file
    speech.save(audio_file_path)
    # Encode the audio file to Base64
    with open(audio_file_path, 'rb') as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

    print(f"AUDIO: {audio_base64}")

    return audio_base64

def main(image_path):
    medical_report = image_to_text(image_path)
    response_list = simplify_text(medical_report)
    translated_text = translate_text(response_list)
    audio_base64 = text_to_speech(translated_text)
    return translated_text, audio_base64

# main()
