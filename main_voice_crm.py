from voice_input import listen_voice
from voice_output import speak
from crm_logic import process_query

while True:

    text = listen_voice()

    if text == "":
        continue

    response = process_query(text)

    print("Bot:", response)

    speak(response)
