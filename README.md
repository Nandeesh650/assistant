# assistant
This is a Python-based Voice Assistant with a graphical user interface (GUI) that combines speech recognition, text-to-speech, and automation capabilities. The assistant can understand voice commands, perform various tasks, and interact with users through both voice and text interfaces.
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
from plyer import notification
import pyautogui
import os
import wikipedia
import warnings
import pywhatkit as pwk

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) 
engine.setProperty('rate',170) 

def speak(Audio):
    engine.say(Audio)
    engine.runAndWait()

def command():
    content = " "
    while content == " ":
       r = sr.Recognizer()
       with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

       try:
         content=r.recognize_google(audio,language='en-in')
         print(" you said....:"+ content)
       except Exception as e:
         print("Please try again..>>>\n")

    return content

def screenshort():
    pyautogui.hotkey('super', 'shift', 's')
def main_process():
    while True:
       request = command().lower()
       if "hello" in request:
          speak("Welcome, how can I help you?")
          #print(request)
       elif "say time" in request:
          now_time= datetime.datetime.now().strftime("%H:%M")
          speak("Current time is "+now_time)
       elif "say date" in request:
          now_date= datetime.datetime.now().strftime("%d:%m")
          speak("Current date is "+now_date)
       elif "new task" in request:
          task = request.replace("new task","")
          task = task.strip()
          if task != "":
             speak("Adding task :"+ task)
             with open ("todolist.txt","a") as file:
                file.write(task + "\n")
       elif "today task" in request:
            with open ("todolist.txt","r") as file:
               speak("today Work  is :"+ file.read())  
       elif "show work" in request:
            with open ("todolist.txt","r") as file:
               tasks = file.read()
            notification.notify(
               title="TO DAY WORKS",
               message = tasks,
            )
       elif "open youtube" in request:
          webbrowser.open("https://www.youtube.com/")
       elif "search google " in request:
          sg = request.replace('search google','')
          webbrowser.open("https://www.google.com/search?q="+sg)
       elif "search wikipedia" in request:
          sw = request.replace('search wikipedia','')
          result=wikipedia.summary(sw,sentences=2)
          speak(result)
          print(result)
       elif "open" in request:
          query =request.replace("open","")
          pyautogui.press("super")
          pyautogui.typewrite(query)
          #pyautogui.sleep(2)
          pyautogui.press("enter")  
          speak(f"AS your request {request}") 
       elif "screenshot" in request:
            screenshot_folder = r'C:\Users\HP\Desktop\project_js\screenshot_folder'
            im1 = pyautogui.screenshot()
            im1.save(os.path.join(screenshot_folder, 'screenshot.png')) 
            speak("srceen short is Don")  
       elif "send whatsapp " in request:
          pwk.sendwhatmsg("+91xxxx7y3601", "Hi", 18, 19,22)
       elif "close" in request:
          query =request.replace("close","")
          pyautogui.hotkey('ctrl', 'w')
          speak(f"AS your request {request}") 
main_process()
Key Technologies Used
pyttsx3 - Text-to-speech engine for voice responses

speech_recognition - Converts speech to text using Google's API

tkinter - Creates the graphical user interface

webbrowser - Handles web navigation

pyautogui - Automates desktop interactions

wikipedia - Fetches information from Wikipedia

pywhatkit - Sends WhatsApp messages

