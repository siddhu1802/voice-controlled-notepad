import speech_recognition as sr
import pyautogui
import time
import os
import subprocess
import psutil
import pyperclip
import threading
import json

pyautogui.FAILSAFE = False

class NotepadController:
    def __init__(self, logger=None):
        self.notepad_open = False
        self.current_file_path = None
        self.script_directory = os.getcwd()
        self.last_command = None
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 150  # Adjust for better sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.commands_file = os.path.join(self.script_directory, "commands.json")
        self.commands = {
            "create": "create a new notepad",
            "open": "open",
            "save": "save the notepad",
            "close": "close notepad"
        }
        self.load_commands()
        self.logger = logger or print  # Use print if no logger is provided

    def load_commands(self):
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.commands.update(data)
            except Exception as e:
                self.logger(f"Failed to load commands: {e}")

    def save_commands(self):
        try:
            with open(self.commands_file, "w", encoding="utf-8") as f:
                json.dump(self.commands, f, indent=2)
        except Exception as e:
            self.logger(f"Failed to save commands: {e}")

    def speech_to_text(self, timeout=5):
        """Convert speech to text."""
        with sr.Microphone() as source:
            try:
                self.logger("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)  # Increase from 2 to 3 seconds
                audio = self.recognizer.listen(source, timeout=timeout)
                return self.recognizer.recognize_google(audio).lower()
            except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError) as e:
                self.logger(f"Error recognizing speech: {e}")
                return None

    def continuous_listen(self, stop_event=None):
        """Continuously listen for speech input, can be stopped by stop_event."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            while True:
                if stop_event and stop_event.is_set():
                    break
                try:
                    self.logger("Listening continuously...")
                    audio = self.recognizer.listen(source, timeout=2)
                    command = self.recognizer.recognize_google(audio).lower()
                    self.logger(f"You said: {command}")
                    return command
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.logger("Could not understand audio, try again.")
                except sr.RequestError as e:
                    self.logger(f"Could not request results; {e}")

    def is_notepad_running(self):
        """Check if Notepad is running."""
        for process in psutil.process_iter(attrs=['name']):
            if process.info['name'].lower() == "notepad.exe":
                return True
        return False

    def close_all_notepads(self):
        """Close all Notepad instances."""
        try:
            subprocess.call(["taskkill", "/F", "/IM", "notepad.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            while self.is_notepad_running():
                time.sleep(1)
            self.notepad_open = False
        except Exception as e:
            self.logger(f"Error closing Notepad: {e}")

    def get_valid_filename(self):
        """Get a valid filename from speech."""
        while True:
            self.logger("\nSay the Notepad name...")
            filename = self.continuous_listen()
            if filename:
                return filename
            self.logger("No name detected! Please say the filename again.")

    def _open_notepad(self, file_path=None):
        """Open Notepad with or without a file."""
        try:
            self.close_all_notepads()
            if file_path:
                subprocess.Popen(["notepad.exe", file_path])
            else:
                subprocess.Popen("notepad.exe")
            time.sleep(2)
        except Exception as e:
            self.logger(f"Error opening Notepad: {e}")

    def create_notepad(self):
        """Create a new Notepad file with the spoken filename and save it automatically."""
        filename = self.get_valid_filename()
        file_path = os.path.join(self.script_directory, f"{filename}.txt")
        
        if os.path.exists(file_path):
            self.logger("Notepad already exists!")
            return
        
        with open(file_path, "w") as f:
            f.write("")  # Create an empty file
        
        subprocess.Popen(["notepad.exe", file_path])  # Open Notepad with the file
        
        self.logger(f"Notepad '{filename}.txt' created and opened successfully!")
        self.notepad_open = True
        self.current_file_path = file_path
        self.last_command = "create"

    def open_notepad(self):
        """Open an existing Notepad file."""
        filename = self.get_valid_filename()
        file_path = os.path.join(self.script_directory, f"{filename}.txt")

        if not os.path.exists(file_path):
            self.logger(f"File '{filename}.txt' does not exist! Please say another name.")
            return

        self._open_notepad(file_path)
        self.logger(f"Opened Notepad file: {filename}.txt")
        self.notepad_open = True
        self.current_file_path = file_path
        self.last_command = "open"

    def save_notepad(self):
        """Save the current Notepad file."""
        if not self.notepad_open:
            self.logger("No Notepad is open to save!")
            return
        try:
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)
            self.logger("Notepad saved successfully.")
            self.last_command = "save"
        except Exception as e:
            self.logger(f"Error saving Notepad: {e}")

    def close_notepad(self):
        """Close Notepad only if the last command was 'save'."""
        if not self.notepad_open:
            self.logger("No Notepad is open to close!")
            return
        
        if self.last_command != "save":
            self.logger("Notepad can only be closed after saving! Writing 'close notepad' instead.")
            self.write_text("close notepad")
            return

        try:
            self.close_all_notepads()
            self.logger("Notepad closed successfully!")
        except Exception as e:
            self.logger(f"Error closing Notepad: {e}")

    def write_text(self, text):
        """Write specified text into Notepad."""
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
        except Exception as e:
            self.logger(f"Error writing to Notepad: {e}")

    def main(self):
        self.logger("Welcome to Voice-Controlled Notepad!")
        self.logger("Available commands:")
        for key, phrase in self.commands.items():
            self.logger(f"  - {phrase}")
        self.logger("  - Speak text to write into Notepad")

        while True:
            text = self.continuous_listen()
            if text:
                text = text.strip().lower()
                cmds = self.commands
                if text == cmds["create"]:
                    self.create_notepad()  # always prompts for filename
                elif text == cmds["open"]:
                    self.open_notepad()    # always prompts for filename
                elif cmds["save"] in text:
                    self.save_notepad()
                elif cmds["close"] in text:
                    self.close_notepad()
                else:
                    self.write_text(text)
            time.sleep(1)

    def create_notepad_with_name(self, filename):
        file_path = os.path.join(self.script_directory, f"{filename}.txt")
        if os.path.exists(file_path):
            self.logger("Notepad already exists!")
            return
        with open(file_path, "w") as f:
            f.write("")
        subprocess.Popen(["notepad.exe", file_path])
        self.logger(f"Notepad '{filename}.txt' created and opened successfully!")
        self.notepad_open = True
        self.current_file_path = file_path
        self.last_command = "create"

    def open_notepad_with_name(self, filename):
        file_path = os.path.join(self.script_directory, f"{filename}.txt")
        if not os.path.exists(file_path):
            self.logger(f"File '{filename}.txt' does not exist! Please say another name.")
            return
        self._open_notepad(file_path)
        self.logger(f"Opened Notepad file: {filename}.txt")
        self.notepad_open = True
        self.current_file_path = file_path
        self.last_command = "open"

if __name__ == "__main__":
    controller = NotepadController()
    controller.main()