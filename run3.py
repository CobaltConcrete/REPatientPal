import os
import requests
import google.generativeai as genai
import translators as ts
from gtts import gTTS
import base64

API_KEY = "AIzaSyAfBEPXr9mrGbMWbb5YkwigTIH_nv2hQ58"

languages = {
    "english": ["en", "en"],
    "chinese": ["zh", "zh"],
    "cantonese": ["yue", "zh-yue"],
    "hindi": ["hi", "hi"]
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

    prompt = f"""
    Assume that you are a very knowledgable and professional medical doctor. You are simplifying a medical report for the elderly who do not understand difficult medical terminology. Simplify this medical report for me, highlighting the important medical terminology. 
    Do not ask for a response or offer clarification.
    Medical Report: {medical_report}
    """

    response = model.generate_content(prompt)

    response_text = response.text
    response_text = response_text.replace("#", "")

    response_list = response_text.split("\n")

    for line in response_list:
        print(line)

    return response_text, response_list

def translate_text(response_text, response_list, lang_code_0):
    translated_text = ""
    non_formatted_translated_text = ""

    ## Translators as ts
    for line in response_list:
        translated_line = ts.translate_text(query_text = line, translator = 'bing', from_language = 'en', to_language = lang_code_0)
        print(translated_line)
        cleaned_translated_line = translated_line.replace("*", "")
        translated_text += cleaned_translated_line
        translated_text += "\n"
        non_formatted_translated_text += translated_line
        non_formatted_translated_text += "\n"

    html_translated_text = translated_text.replace("\n", "<br>")
    combined_text = "English: \n" + response_text + "\n Translated: \n" + html_translated_text

    non_formatted_combined_text = "English: \n" + response_text + "\n Translated: \n" + non_formatted_translated_text
    html_combined_text = non_formatted_combined_text.replace("\n", "<br>")
    html_combined_text = html_combined_text.replace("\n\n", "</p><p>").replace("English:", "<h1>English:</h1>").replace("Translated:", "<h1>Translated:</h1>")
    text_length = len(html_combined_text)
    for i in range(text_length):
        html_combined_text = html_combined_text.replace("**", "<strong>", 1).replace("**", "</strong>", 1)

    return html_translated_text, html_combined_text

def text_to_speech(chinese_text, lang_code_1):
    audio_file_path = "C:\Save Data Here\Coding stuff\Projects\REPatientPal\outputwebsite.mp3"

    # Language in which you want to convert
    language = lang_code_1

    # Remove the HTML separators
    chinese_text = chinese_text.replace("<br>", "")

    # Creating an object for gTTS
    speech = gTTS(text=chinese_text, lang=language)

    # Saving the converted audio in a mp3 file
    speech.save(audio_file_path)
    # Encode the audio file to Base64
    with open(audio_file_path, 'rb') as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

    # print(f"AUDIO: {audio_base64}")

    return audio_base64

def main(image_path, language):
    medical_report = image_to_text(image_path)
    response_text, response_list = simplify_text(medical_report)
    html_translated_text, html_combined_text = translate_text(response_text, response_list, languages[language][0])
    audio_base64 = text_to_speech(html_translated_text, languages[language][1])
    return html_combined_text, audio_base64

# main()
