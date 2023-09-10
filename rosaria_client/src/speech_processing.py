import speech_recognition as sr
import pyttsx3
import os
import time
from random import randint
import smtplib, ssl

#Define global variables
tts_engine= pyttsx3.init()
password = "0000"

def generate_password_and_email():

    secret_code = randint(1000, 9999)     # randint is inclusive at both ends
    email_from = 'catalin_sender1234@gmail.com'
    password = 'myzwe9-ruxMut-qosbap'
    email_to = 'catalin_receiver1234@gmail.com'

    # Connect to Gmail's SMTP Outgoing Mail server with such context
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        # Provide Gmail's login information
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(email_from, password)
        # Send mail with from_addr, to_addrs, msg, which were set up as variables above
        subject = "Your online order is on the way!"
        body = f"Thanks for your online order. Your secret code to receive the package is {secret_code}"
        email_string = f'Subject: {subject}\n\n {body}'

        smtp.sendmail(email_from, email_to, email_string)

    return str(secret_code)



def speech_detection(password_detection_mode):

    recogniser = sr.Recognizer()
     #The engine for the text to speech...
    #https://stackoverflow.com/questions/65660897/pyttsx3-unknown-voice-id
    #voices = tts_engine.getProperty('voices')
    if password_detection_mode == True:
        tts_engine.say("Greeting human, please let me know the secret password to prove you are the intended receipient.")
        tts_engine.runAndWait()
    else:
        #tts_engine.say("Greeting human, please let me know your answer.")
        #tts_engine.runAndWait()
        pass
    while True:

        try:
            with sr.Microphone() as mic:
                recogniser.adjust_for_ambient_noise(mic,duration=0.2)
                audio=recogniser.listen(mic)

                detected_speech = recogniser.recognize_google(audio)
                detected_speech = detected_speech.lower()

                print(f"Detected speech: {detected_speech}")
                return detected_speech


        except sr.UnknownValueError():
            recogniser = sr.Recognizer()
            continue

    print("Finished speech detection")

    return detected_speech

def encountered_person_pipeline():

    encountered_person_password_attempt = speech_detection(password_detection_mode=True)
    recipient_person_found = False
    if encountered_person_password_attempt == password:
        tts_engine.say("You are the intended recipient, here is your package!")
        tts_engine.runAndWait()
        recipient_person_found = True
    else:
        tts_engine.say("Incorrect password, please try again!")
        tts_engine.runAndWait()
        time.sleep(1)

        answer = speech_detection(password_detection_mode=False)

        if answer == password:
                tts_engine.say("You are the intended recipient, here is your package!")
                tts_engine.runAndWait()
                recipient_person_found = True
        else:
            tts_engine.say("Incorrect again, please leave the room!")
            tts_engine.runAndWait()
            time.sleep(10)


    return recipient_person_found
#Driving code
if __name__ == "__main__":

    timeout= 500 #Seconds
    timeout_start = time.time()
    password=generate_password_and_email()
    recipient_person_found = encountered_person_pipeline()


