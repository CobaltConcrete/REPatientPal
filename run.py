import os
import requests
import google.generativeai as genai
import translators as ts

API_KEY = ""

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

## Translators as ts
for line in response_list:
    print(ts.translate_text(query_text = line, translator = 'bing', from_language = 'en', to_language = 'zh'))




## Google Translate mk1

# translate_client = translate.Client()

# result = translate_client.translate(
#     response_text, target_language='zh-TW')

# print(result['translatedText'])

