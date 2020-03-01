import speech_recognition as sr
import time
import asyncio
import abc

class superClassVoice(abc.ABC):
    def __init__(self):
        self.speech = ""
        self.clearSpeech = False
        self.QMove= [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.QStop = [0,0]
        self.running = True

    @abc.abstractmethod
    def voiceComms(self):
        pass

class voiceIntegrationBack(superClassVoice):

    def __init__(self):
        super(voiceIntegrationBack, self).__init__()

    def voiceComms(self):
        while self.running:
            r = sr.Recognizer()
            mic = sr.Microphone()
            with mic as source:
                print("Please speak")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                try:
                    self.speech = r.recognize_google(audio)
                    print("Data taken in")
                    self.clearSpeech = True
                    print(self.speech)
                    if "Move".lower() in self.speech.lower() or "Stop".lower() in self.speech.lower():
                        time.sleep(30)
                except sr.UnknownValueError:
                    self.clearSpeech = False
                    print("Not understood error value, try again please")
                except sr.RequestError:
                    self.clearSpeech = False
                    print("REQ Not understood, try again please")

class voiceIntegration(superClassVoice):

   def __init__(self):
       super(voiceIntegration, self).__init__()

   async def voiceComms(self):
        self.speech = ""
        r = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            print("Please speak FOR THE SCORE")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                print("Time to recog SCORE")
                self.speech = r.recognize_google(audio)
                self.clearSpeech = True
                print(self.speech)
            except sr.UnknownValueError:
                self.clearSpeech = False
                print("Not understood error value, try again please")
            except sr.RequestError:
                self.clearSpeech = False
                print("REQ Not understood, try again please")
            except asyncio.TimeoutError:
                self.clearSpeech = False
                print("Timed out")

