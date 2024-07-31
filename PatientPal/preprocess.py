import os
import requests
import google.generativeai as genai
import translators as ts
from gtts import gTTS

API_KEY = "AIzaSyAfBEPXr9mrGbMWbb5YkwigTIH_nv2hQ58"

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

def translate_text(reponse_list):
    chinese_text = ""

    ## Translators as ts
    for line in response_list:
        translated_line = ts.translate_text(query_text = line, translator = 'bing', from_language = 'en', to_language = 'yue')
        print(translated_line)
        cleaned_translated_line = translated_line.replace("*", "")
        chinese_text += cleaned_translated_line
        chinese_text += "\n"

    return chinese_text

def text_to_speech(chinese_text):
    # Language in which you want to convert
    language = "zh-yue"

    # Creating an object for gTTS
    speech = gTTS(text=chinese_text, lang=language)

    # Saving the converted audio in a mp3 file
    speech.save("output2.mp3")

    return speech

def main():
    medical_report = image_to_text("Screenshot 2024-07-29 155146.png")
    response_list = simplify_text(medical_report)
    translated_text = translate_text(response_list)
    speech = text_to_speech(translated_text)
    return translated_text, speech

