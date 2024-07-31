import os
import requests
import google.generativeai as genai
import translators as ts
from gtts import gTTS


API_KEY = "AIzaSyAfBEPXr9mrGbMWbb5YkwigTIH_nv2hQ58"

api_url = 'https://api.api-ninjas.com/v1/imagetotext'
image_file_descriptor = open('Screenshot 2024-07-29 155146.png', 'rb')
files = {'image': image_file_descriptor}
r = requests.post(api_url, files=files)
# print(r.json())

medical_report = r.json()

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

chinese_text = ""

## Translators as ts
for line in response_list:
    translated_line = ts.translate_text(query_text = line, translator = 'bing', from_language = 'en', to_language = 'zh')
    print(translated_line)
    cleaned_translated_line = translated_line.replace("*", "")
    chinese_text += cleaned_translated_line
    chinese_text += "\n"


# Text to be converted to audio
text = "Hello, this is a text to speech conversion example."

# Language in which you want to convert
language = "zh-CN"

# Creating an object for gTTS
speech = gTTS(text=chinese_text, lang=language, slow=False)

# Saving the converted audio in a mp3 file
speech.save("output2.mp3")
