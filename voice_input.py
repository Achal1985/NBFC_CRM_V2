import speech_recognition as sr

def listen_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        

    try:
        text = r.recognize_google(audio, language="hi-IN")  # Hindi support
        print("You said:", text)
        return text
    except:
        return "Sorry, could not understand"
