import speech_recognition as sr
import cozmo
import threading

class voiceRecognition:

    def voiceCommsAction(self,robot:cozmo.robot.Robot):
        lock = threading.Lock()
        while True:
            speech = self.voiceComms()
            if "Cozmo".lower() in speech.lower() or "Cosmo".lower() in speech.lower():
                lock.acquire()
                robot.say_text("Hello nice to meet you")
                lock.release()

    def voiceComms(self):
        r = sr.Recognizer()
        mic = sr.Microphone()
        speech = ""
        with mic as source:
            print("Please speak")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                speech = r.recognize_google(audio)
                print(speech)
            except sr.UnknownValueError:
                print("Not understood, try again please")
            except sr.RequestError:
                print("Not understood, try again please")
            return speech


#cozmo.run_program(voiceCommsAction)
