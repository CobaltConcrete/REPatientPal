from gtts import gTTS
import os






















# Text to be converted to audio
text = "Hello, this is a text to speech conversion example."

# Language in which you want to convert
language = 'en'

# Creating an object for gTTS
speech = gTTS(text=text, lang=language, slow=False)

# Saving the converted audio in a mp3 file
speech.save("output.mp3")

# Playing the converted file
# os.system("start output.mp3")  # For Windows
# os.system("afplay output.mp3")  # For Mac
# os.system("mpg321 output.mp3")  # For Linux
