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
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from PIL import Image, ImageTk
import sys

# Suppress warnings
warnings.filterwarnings("ignore")

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id) 
        self.engine.setProperty('rate', 170)
        
        # Control variables
        self.is_listening = False
        self.assistant_active = True
        
        self.setup_gui()
        
    def setup_gui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#34495E', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Voice Assistant", 
                              font=('Arial', 20, 'bold'), 
                              fg='#ECF0F1', bg='#34495E')
        title_label.pack(pady=20)
        
        # Main Content Frame
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left Frame - Controls
        left_frame = tk.Frame(main_frame, bg='#34495E', width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Right Frame - Output
        right_frame = tk.Frame(main_frame, bg='#2C3E50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Controls Section
        controls_label = tk.Label(left_frame, text="Controls", 
                                 font=('Arial', 14, 'bold'), 
                                 fg='#ECF0F1', bg='#34495E')
        controls_label.pack(pady=10)
        
        # Listen Button
        self.listen_btn = tk.Button(left_frame, text="🎤 Start Listening", 
                                   font=('Arial', 12), 
                                   bg='#27AE60', fg='white',
                                   command=self.toggle_listening,
                                   width=15, height=2)
        self.listen_btn.pack(pady=10)
        
        # Status Indicator
        status_frame = tk.Frame(left_frame, bg='#34495E')
        status_frame.pack(pady=10)
        
        status_label = tk.Label(status_frame, text="Status:", 
                               font=('Arial', 10), 
                               fg='#ECF0F1', bg='#34495E')
        status_label.pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(status_frame, text="●", 
                                        font=('Arial', 12), 
                                        fg='#E74C3C', bg='#34495E')
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        
        # Quick Actions
        actions_label = tk.Label(left_frame, text="Quick Actions", 
                                font=('Arial', 12, 'bold'), 
                                fg='#ECF0F1', bg='#34495E')
        actions_label.pack(pady=(20, 10))
        
        # Quick action buttons
        actions = [
            ("🕐 Get Time", self.get_time),
            ("📅 Get Date", self.get_date),
            ("📋 Show Tasks", self.show_tasks),
            ("📸 Take Screenshot", self.take_screenshot),
            ("❌ Exit", self.exit_app)
        ]
        
        for text, command in actions:
            btn = tk.Button(left_frame, text=text, 
                          font=('Arial', 10), 
                          bg='#3498DB', fg='white',
                          command=command, width=15)
            btn.pack(pady=5)
        
        # Output Section
        output_label = tk.Label(right_frame, text="Assistant Output", 
                               font=('Arial', 14, 'bold'), 
                               fg='#ECF0F1', bg='#2C3E50')
        output_label.pack(pady=(0, 10))
        
        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            right_frame, 
            wrap=tk.WORD, 
            width=60, 
            height=15,
            font=('Arial', 10),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.config(state=tk.DISABLED)
        
        # Input Frame
        input_frame = tk.Frame(right_frame, bg='#2C3E50')
        input_frame.pack(fill=tk.X, pady=10)
        
        self.input_entry = tk.Entry(input_frame, font=('Arial', 12), width=50)
        self.input_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_text_command)
        
        send_btn = tk.Button(input_frame, text="Send", 
                           font=('Arial', 12), 
                           bg='#3498DB', fg='white',
                           command=self.send_text_command)
        send_btn.pack(side=tk.LEFT)
        
        # Add initial message
        self.add_to_conversation("Assistant", "Hello! I'm your voice assistant. Click 'Start Listening' or type your command.")
        
    def add_to_conversation(self, speaker, message):
        self.conversation_text.config(state=tk.NORMAL)
        self.conversation_text.insert(tk.END, f"\n{speaker}: {message}\n")
        self.conversation_text.config(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
        
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_btn.config(text="⏸️ Stop Listening", bg='#E74C3C')
            self.status_indicator.config(fg='#27AE60')
            self.add_to_conversation("System", "Started listening...")
            # Start listening in a separate thread
            threading.Thread(target=self.voice_command_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.listen_btn.config(text="🎤 Start Listening", bg='#27AE60')
            self.status_indicator.config(fg='#E74C3C')
            self.add_to_conversation("System", "Stopped listening")
    
    def voice_command_loop(self):
        while self.is_listening and self.assistant_active:
            command_text = self.command()
            if command_text and self.is_listening:
                self.process_command(command_text)
    
    def send_text_command(self, event=None):
        command_text = self.input_entry.get().strip()
        if command_text:
            self.add_to_conversation("You", command_text)
            self.input_entry.delete(0, tk.END)
            self.process_command(command_text)
    
    def speak(self, audio):
        self.add_to_conversation("Assistant", audio)
        self.engine.say(audio)
        self.engine.runAndWait()
    
    def command(self):
        content = " "
        while content == " " and self.is_listening:
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    self.root.after(0, self.add_to_conversation, "System", "Listening...")
                    r.adjust_for_ambient_noise(source, duration=0.2)
                    audio = r.listen(source, timeout=5)
                
                try:
                    content = r.recognize_google(audio, language='en-in')
                    self.root.after(0, self.add_to_conversation, "You", content)
                except sr.UnknownValueError:
                    self.root.after(0, self.add_to_conversation, "System", "Could not understand audio")
                    content = " "
                except sr.RequestError as e:
                    self.root.after(0, self.add_to_conversation, "System", f"Error with speech recognition: {e}")
                    content = " "
                except sr.WaitTimeoutError:
                    continue
                    
            except Exception as e:
                self.root.after(0, self.add_to_conversation, "System", f"Error: {str(e)}")
                content = " "

        return content.lower() if content != " " else ""

    def process_command(self, request):
        request = request.lower()
        
        if "hello" in request:
            self.speak("Welcome, how can I help you?")
        elif "say time" in request or "time" in request:
            now_time = datetime.datetime.now().strftime("%H:%M")
            self.speak("Current time is " + now_time)
        elif "say date" in request or "date" in request:
            now_date = datetime.datetime.now().strftime("%d:%m")
            self.speak("Current date is " + now_date)
        elif "new task" in request:
            task = request.replace("new task", "").strip()
            if task:
                self.speak("Adding task: " + task)
                with open("todolist.txt", "a") as file:
                    file.write(task + "\n")
        elif "today task" in request or "show tasks" in request:
            try:
                with open("todolist.txt", "r") as file:
                    tasks = file.read()
                    if tasks:
                        self.speak("Today's work is: " + tasks)
                    else:
                        self.speak("No tasks for today")
            except FileNotFoundError:
                self.speak("No task file found")
        elif "show work" in request:
            try:
                with open("todolist.txt", "r") as file:
                    tasks = file.read()
                notification.notify(
                    title="TO DAY WORKS",
                    message=tasks,
                    timeout=10
                )
                self.speak("Notification sent with today's work")
            except FileNotFoundError:
                self.speak("No task file found")
        elif "open youtube" in request:
            webbrowser.open("https://www.youtube.com/")
            self.speak("Opening YouTube")
        elif "search google" in request:
            sg = request.replace('search google', '').strip()
            if sg:
                webbrowser.open("https://www.google.com/search?q=" + sg)
                self.speak(f"Searching Google for {sg}")
        elif "search wikipedia" in request:
            sw = request.replace('search wikipedia', '').strip()
            if sw:
                try:
                    result = wikipedia.summary(sw, sentences=2)
                    self.speak(result)
                except wikipedia.exceptions.DisambiguationError as e:
                    self.speak("There are multiple results. Please be more specific.")
                except wikipedia.exceptions.PageError:
                    self.speak("No Wikipedia page found for that query.")
        elif "open" in request:
            query = request.replace("open", "").strip()
            if query:
                pyautogui.press("super")
                pyautogui.typewrite(query)
                pyautogui.press("enter")
                self.speak(f"As your request {request}")
        elif "screenshot" in request:
            try:
                screenshot_folder = r'C:\Users\HP\Desktop\project_js\screenshot_folder'
                os.makedirs(screenshot_folder, exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                im1 = pyautogui.screenshot()
                im1.save(os.path.join(screenshot_folder, filename))
                self.speak("Screenshot is done")
            except Exception as e:
                self.speak(f"Error taking screenshot: {str(e)}")
        elif "send whatsapp" in request:
            try:
                pwk.sendwhatmsg("+917204763601", "Hi", 18, 19, 22)
                self.speak("WhatsApp message sent")
            except Exception as e:
                self.speak(f"Error sending WhatsApp message: {str(e)}")
        elif "close" in request:
            query = request.replace("close", "").strip()
            pyautogui.hotkey('ctrl', 'w')
            self.speak(f"As your request {request}")
        else:
            self.speak("I didn't understand that command. Please try again.")

    # Quick action methods
    def get_time(self):
        now_time = datetime.datetime.now().strftime("%H:%M")
        self.speak("Current time is " + now_time)
    
    def get_date(self):
        now_date = datetime.datetime.now().strftime("%d:%m")
        self.speak("Current date is " + now_date)
    
    def show_tasks(self):
        try:
            with open("todolist.txt", "r") as file:
                tasks = file.read()
                if tasks:
                    self.speak("Today's work is: " + tasks)
                else:
                    self.speak("No tasks for today")
        except FileNotFoundError:
            self.speak("No task file found")
    
    def take_screenshot(self):
        try:
            screenshot_folder = r'C:\Users\HP\Desktop\project_js\screenshot_folder'
            os.makedirs(screenshot_folder, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            im1 = pyautogui.screenshot()
            im1.save(os.path.join(screenshot_folder, filename))
            self.speak("Screenshot is done")
        except Exception as e:
            self.speak(f"Error taking screenshot: {str(e)}")
    
    def exit_app(self):
        self.assistant_active = False
        self.is_listening = False
        if messagebox.askokcancel("Quit", "Do you want to exit the Voice Assistant?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()