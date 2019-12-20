    # import speech_recognition as sr
    # r = sr.Recognizer()
    # mic = sr.Microphone()
    # with mic as source:
    #     print("Speak")
    #     r.adjust_for_ambient_noise(source)
    #     audio = r.listen(source)
    #     speech = r.recognize_google(audio)
    #     print(speech)


import speech_recognition as sr
import noisereduce as nr
import wave
import contextlib
import math
import scipy
from scipy.io import wavfile


# obtain audio from the microphone
r = sr.Recognizer()
clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
with clip as source:
    audio = r.record(source)
    print("data loaded")
    result = r.recognize_google(audio)
    if("stop" in result):
        print("KOBE")
    else:
        print("CURRY")
    print(result)










    # with sr.Microphone() as source:
    #     print("Please wait. Calibrating microphone...")
    #     # listen for 5 seconds and create the ambient noise energy level
    #     r.adjust_for_ambient_noise(source, duration=15)
    #     print("Say something!")
    #     audio = r.listen(source,None,5)
    #     with open("microphone-results.wav", "wb") as f:
    #          f.write(audio.get_wav_data())
    #     length = 0
    #     fileName = "microphone-results.wav"
    #     numpyFile = wavfile.read(fileName)
    #     with contextlib.closing(wave.open(fileName,'r')) as f:
    #         frames = f.getnframes()
    #         rate = f.getframerate()
    #         length = frames / float(rate)
    #     length = math.ceil(length)
    #     noisy_part = fileName[0:length]
    #     reduced_noise = nr.reduce_noise(audio_clip=numpyFile, noise_clip=noisy_part, verbose=True)
    #     with open("microphone-results.wav", "wb") as f:
    #          f.write(reduced_noise)
    #     print("Done")
    #
    #
    #
    #         #command = r.recognize_google(audio)
    # # recognize speech using Sphinx2
    # try:
    #     print("Sphinx thinks you said '" + r.recognize_sphinx(audio) + "'")
    # except sr.UnknownValueError:
    #     print("Sphinx could not understand audio")
    # except sr.RequestError as e:
    #     print("Sphinx error; {0}".format(e))