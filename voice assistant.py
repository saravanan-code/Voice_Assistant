# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 15:35:50 2021

@author: Saravanan

"""
from datetime import datetime
import pickle
import wikipedia
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import webbrowser as wb
import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import smtplib





SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october","november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]
chrome_path= 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'

options = webdriver.ChromeOptions() 
options.add_argument("user-data-dir=C:/Users/" + getpass.getuser() + "/AppData/Local/Google/Chrome/User Data")
driver = webdriver.Chrome(executable_path="C:/webdrivers/chromedriver.exe", options=options)


def music(song):
    speak("1 second")
    driver.get("https://www.youtube.com/results?search_query=" + song)
    delay = 3
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'video-title')))
    driver.find_element_by_css_selector("a[id='video-title']").click()
    speak("Enjoy " + song)

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()



    
uid = "nscetcse23@gmail.com"
upwd = "9210191040"
server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(uid,upwd)


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    # THE NEW PART STARTS HERE
    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    # This is slighlty different from the video but the correct version
    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:  # FIXED FROM VIDEO
        return datetime.date(month=month, day=day, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])


WAKE = "star"
SERVICE = authenticate_google()
print("Start")

while True:
    print("Listening")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("yes")
        text = get_audio()

        CALENDAR_STRS = ["do i have", "do i have plans", "am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I don't understand")

        NOTE_STRS = ["make a note", "write this down", "remember this"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of that.")
                
        google = ["open google","open chrome","browser","google","search"]
        for phrase in google:
            if phrase in text:
               speak("what to search")
               search = get_audio()
               try:
                   wb.get(chrome_path).open("https://www.google.com/search?q="+search)
                   speak("searching......")
               except Exception:
                   print("I don't understand")
        signals = ["open signal","signal app"]
        for phrase in signals:
            if phrase in text:
                subprocess.Popen(r'C:\Users\techn\AppData\Local\Programs\signal-desktop/Signal.exe')
                speak("opening signal......")
        firefoxs = ["open firefox","firefox app"]
        for phrase in firefoxs:
            if phrase in text:
                subprocess.Popen('C:\Program Files\Mozilla Firefox\firefox.exe')
                speak("opening firefox..........")
        wiki = ["search wiki","wiki search"]
        for phrase in wiki:
            if phrase in text:
                speak("say specific word to search")
                sec = get_audio()
                try:
                    speak(wikipedia.summary(sec, sentences = 3))
                except Exception:
                    print ("I don't understand")
        greeting = ["hi","how are you","how are you doing","hey there"]
        for phrase in greeting:
            if phrase in text:
                speak("nice and fine")
        if "time now" in text:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(current_time)
            speak(current_time)
        if "date" in text:
            now = datetime.now() 
            print("now =", now)
            dt_string = now.strftime("%d/%m/%Y")
            speak(dt_string)
        mail = ["send mail","mail"]
        for phrase in mail:
            if phrase in text:
                speak("whom to send")
                mailr=get_audio()
                if "manoj kumar" in mailr:
                    re = "smk11500@gmail.com"
                    speak("what to send")
                    textt=get_audio()
                    server.sendmail("nscetcse23@gmail.com",re,textt)
                    server.quit()
                    speak("mail sended........")
        lang = ["in what language you are created","you are created using","programmed using","in what programming language you are created"]    
        for phrase in lang:
            if phrase in text:
                speak("i was created using python")        
        if "ok" in text :
            speak("what ok")
        if "tell me a joke" in text:
            speak("i am serious kind of person i dont tell joke")
        if "what is your name" in text:
            speak("my name is star")
        if "who are you" in text:
            speak("i am an voice assistant")
        if "how are you" in text:
            speak("i am fine , what do you want")
        if "thank you" in text:
            speak("you are welcome")
        if "what are you doing" in text:
            speak("nothing, like you")
        if "do you belive in god" in text:
            speak("i only belive in science")
        if "better than cortana" in text:
            speak("ofcourse, i am ")
        if "play" in text:
            music(text.split('play')[1])
        if "who is your favourite singer" in text:
            speak("celine dion is my favourite singer")
        if "what is your favourite movie" in text:
            speak("i like avengers end game")
        if "who is your favourite actress" in text:
            speak("of course kate winslet")
        if "say something" in text:
            speak("i am not your crush to say something")
        if "who is your favourite actor" in text:
            speak("Robert Downey junior")
        if "who created you" in text:
            speak("saravanan")
       
        if "i want a apple" in text:
            speak("go and pick yourself")
        if "solve a problem" in text:
            speak("you want solve your problem")
        if "why are you here" in text:
            speak("because you brought me here")
            
        




