import base64

audio_file_path = "C:\Save Data Here\Coding stuff\Projects\REPatientPal\output.mp3"

with open(audio_file_path, 'rb') as audio_file:
    audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

print(f"AUDIO: {audio_base64}")