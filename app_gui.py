import customtkinter as ctk
import threading
import os
import json
from hcidublicate import NotepadController

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.title("Settings")
        self.geometry("350x300")
        self.controller = controller

        # Voice Sensitivity
        ctk.CTkLabel(self, text="Voice Sensitivity:").pack(pady=(20, 0))
        self.sensitivity_slider = ctk.CTkSlider(self, from_=50, to=400, number_of_steps=70)
        self.sensitivity_slider.set(self.controller.recognizer.energy_threshold)
        self.sensitivity_slider.pack(pady=10)
        self.sensitivity_slider.bind("<ButtonRelease-1>", self.update_sensitivity)

        # Default Folder
        ctk.CTkLabel(self, text="Default Notes Folder:").pack(pady=(20, 0))
        self.folder_entry = ctk.CTkEntry(self, width=200)
        self.folder_entry.insert(0, self.controller.script_directory)
        self.folder_entry.pack(pady=5)
        ctk.CTkButton(self, text="Browse", command=self.browse_folder).pack(pady=2)

        # Dark Mode Toggle
        self.dark_mode_var = ctk.BooleanVar(value=ctk.get_appearance_mode() == "dark")
        self.dark_mode_check = ctk.CTkCheckBox(self, text="Dark Mode", variable=self.dark_mode_var, command=self.toggle_dark_mode)
        self.dark_mode_check.pack(pady=10)

        # Hotkey Info (display only)
        ctk.CTkLabel(self, text="Hotkey: F9 to Start/Stop Listening (coming soon)").pack(pady=10)

        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=10)

    def update_sensitivity(self, event=None):
        value = int(self.sensitivity_slider.get())
        self.controller.recognizer.energy_threshold = value

    def browse_folder(self):
        import tkinter.filedialog as fd
        folder = fd.askdirectory()
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.controller.script_directory = folder

    def toggle_dark_mode(self):
        ctk.set_appearance_mode("dark" if self.dark_mode_var.get() else "light")

class LogsDialog(ctk.CTkToplevel):
    def __init__(self, master, logs):
        super().__init__(master)
        self.title("Logs")
        self.geometry("400x400")
        log_box = ctk.CTkTextbox(self, state="normal")
        log_box.pack(expand=True, fill="both", padx=10, pady=10)
        log_box.insert("end", "\n".join(logs))
        log_box.configure(state="disabled")

class VoiceNotepadApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voice Notepad Automation")
        self.geometry("420x650")
        ctk.set_appearance_mode("system")

        # Controller
        self.controller = NotepadController(logger=self.log)
        self.listening = False
        self.listen_thread = None
        self.stop_event = threading.Event()
        self.logs = []

        self.load_settings()  # <-- Load settings before building UI

        # Main content frame (for swapping screens)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True)
        self.show_home()

    def show_home(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Header
        self.header = ctk.CTkLabel(self.content_frame, text="🎙️ Voice Notepad Automation", font=("Arial", 22, "bold"))
        self.header.pack(pady=(20, 10))
        # Status Frame
        self.status_frame = ctk.CTkFrame(self.content_frame)
        self.status_frame.pack(padx=20, pady=10, fill="x")
        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: Idle", font=("Arial", 14))
        self.status_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.last_command_label = ctk.CTkLabel(self.status_frame, text="Last command: None", font=("Arial", 12))
        self.last_command_label.pack(anchor="w", padx=10)
        self.current_file_label = ctk.CTkLabel(self.status_frame, text="Current file: None", font=("Arial", 12))
        self.current_file_label.pack(anchor="w", padx=10, pady=(0, 10))
        # Buttons
        self.start_btn = ctk.CTkButton(self.content_frame, text="Start Listening", command=self.start_listening)
        self.start_btn.pack(pady=5, fill="x", padx=60)
        self.stop_btn = ctk.CTkButton(self.content_frame, text="Stop Listening", command=self.stop_listening)
        self.stop_btn.pack(pady=5, fill="x", padx=60)
        self.open_folder_btn = ctk.CTkButton(self.content_frame, text="Open Notepad Folder", command=self.open_folder)
        self.open_folder_btn.pack(pady=5, fill="x", padx=60)
        self.settings_btn = ctk.CTkButton(self.content_frame, text="Settings", command=self.show_settings)
        self.settings_btn.pack(pady=5, fill="x", padx=60)
        self.controls_btn = ctk.CTkButton(self.content_frame, text="Controls", command=self.show_controls)
        self.controls_btn.pack(pady=5, fill="x", padx=60)
        # Logs/History
        self.log_box = ctk.CTkTextbox(self.content_frame, height=100, state="disabled")
        self.log_box.pack(padx=20, pady=10, fill="both", expand=False)
        # Footer
        self.autostart_var = ctk.BooleanVar(value=False)
        self.autostart_check = ctk.CTkCheckBox(
            self.content_frame, text="Start automatically on system boot", variable=self.autostart_var
        )
        self.autostart_check.pack(anchor="w", padx=30, pady=(10, 0))
        self.view_logs_link = ctk.CTkButton(self.content_frame, text="View Logs", fg_color="transparent", text_color="blue", command=self.view_logs)
        self.view_logs_link.pack(anchor="e", padx=30, pady=(0, 10))
        # Start listening automatically on launch
        self.start_listening()

    def show_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Always reload settings from file before showing
        self.load_settings()
        
        # Back button at top left with arrow
        back_btn = ctk.CTkButton(
            self.content_frame, text="← Back", width=80, command=self.show_home
        )
        back_btn.pack(anchor="w", padx=10, pady=(10, 0))

        ctk.CTkLabel(self.content_frame, text="Settings", font=("Arial", 18, "bold")).pack(pady=(10, 10))

        # Voice Sensitivity
        ctk.CTkLabel(self.content_frame, text="Voice Sensitivity:").pack(pady=(20, 0))
        self.sensitivity_slider = ctk.CTkSlider(self.content_frame, from_=50, to=400, number_of_steps=70)
        self.sensitivity_slider.set(self.controller.recognizer.energy_threshold)
        self.sensitivity_slider.pack(pady=10)
        self.sensitivity_slider.bind("<ButtonRelease-1>", self.update_sensitivity)

        self.sensitivity_value_label = ctk.CTkLabel(self.content_frame, text=str(self.sensitivity_slider.get()))
        self.sensitivity_value_label.pack()
        self.sensitivity_slider.configure(command=lambda v: self.sensitivity_value_label.configure(text=str(int(float(v)))))

        # Default Folder
        ctk.CTkLabel(self.content_frame, text="Default Notes Folder:").pack(pady=(20, 0))
        self.folder_entry = ctk.CTkEntry(self.content_frame, width=200)
        self.folder_entry.insert(0, self.controller.script_directory)
        self.folder_entry.pack(pady=5)
        ctk.CTkButton(self.content_frame, text="Browse", command=self.browse_folder).pack(pady=2)

        # Dark Mode Toggle
        appearance_mode = ctk.get_appearance_mode().lower()
        self.dark_mode_var = ctk.BooleanVar(value=(appearance_mode == "dark"))
        self.dark_mode_check = ctk.CTkCheckBox(
            self.content_frame, text="Dark Mode", variable=self.dark_mode_var, command=self.toggle_dark_mode
        )
        self.dark_mode_check.pack(pady=10)

        # Reset Settings Button
        ctk.CTkButton(self.content_frame, text="Reset Settings to Default", command=self.reset_settings).pack(pady=5)
        # Reset Commands Button
        ctk.CTkButton(self.content_frame, text="Reset Voice Commands to Default", command=self.reset_commands).pack(pady=5)

        # Save Settings Button
        ctk.CTkButton(self.content_frame, text="Save Settings", command=self.save_settings).pack(pady=5)

        # Hotkey Info (display only)
        ctk.CTkLabel(self.content_frame, text="Hotkey: F9 to Start/Stop Listening (coming soon)").pack(pady=10)

        # App Version (example)
        ctk.CTkLabel(self.content_frame, text="App Version: 1.0.0").pack(pady=5)

        # Back Button
        ctk.CTkButton(self.content_frame, text="Back", command=self.show_home).pack(pady=10)

    def update_sensitivity(self, event=None):
        value = int(self.sensitivity_slider.get())
        self.controller.recognizer.energy_threshold = value

    def browse_folder(self):
        import tkinter.filedialog as fd
        folder = fd.askdirectory()
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.controller.script_directory = folder

    def toggle_dark_mode(self):
        ctk.set_appearance_mode("dark" if self.dark_mode_var.get() else "light")

    def reset_settings(self):
        # Reset sensitivity and folder to defaults
        self.controller.recognizer.energy_threshold = 150
        self.sensitivity_slider.set(150)
        default_folder = os.getcwd()
        self.controller.script_directory = default_folder
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, default_folder)
        self.dark_mode_var.set(False)
        self.toggle_dark_mode()

    def reset_commands(self):
        # Reset commands to default and save
        self.controller.commands = {
            "create": "create a new notepad",
            "open": "open",
            "save": "save the notepad",
            "close": "close notepad"
        }
        self.controller.save_commands()
        ctk.CTkLabel(self.content_frame, text="Voice commands reset to default!", text_color="green").pack()

    def save_settings(self):
        settings = {
            "energy_threshold": int(self.sensitivity_slider.get()),
            "notes_folder": self.folder_entry.get(),
            "dark_mode": self.dark_mode_var.get(),
            "autostart": self.autostart_var.get()
        }
        with open(self.get_settings_path(), "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        self.controller.recognizer.energy_threshold = settings["energy_threshold"]
        self.controller.script_directory = settings["notes_folder"]
        ctk.set_appearance_mode("dark" if settings["dark_mode"] else "light")
        ctk.CTkLabel(self.content_frame, text="Settings saved!", text_color="green").pack()

    def load_settings(self):
        try:
            with open(self.get_settings_path(), "r", encoding="utf-8") as f:
                settings = json.load(f)
            self.controller.recognizer.energy_threshold = settings.get("energy_threshold", 150)
            self.controller.script_directory = settings.get("notes_folder", os.getcwd())
            if settings.get("dark_mode", False):
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
            self.autostart_var = ctk.BooleanVar(value=settings.get("autostart", False))
        except Exception:
            self.controller.recognizer.energy_threshold = 150
            self.controller.script_directory = os.getcwd()
            self.autostart_var = ctk.BooleanVar(value=False)

    def get_settings_path(self):
        return os.path.join(os.getcwd(), "settings.json")

    def show_controls(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Back button at top left with arrow
        back_btn = ctk.CTkButton(
            self.content_frame, text="← Back", width=80, command=self.show_home
        )
        back_btn.pack(anchor="w", padx=10, pady=(10, 0))

        ctk.CTkLabel(self.content_frame, text="Customize Voice Commands", font=("Arial", 18, "bold")).pack(pady=(20, 10))

        self.command_vars = {}
        for key, label in [
            ("create", "Create Notepad"),
            ("open", "Open Notepad"),
            ("save", "Save Notepad"),
            ("close", "Close Notepad"),
        ]:
            ctk.CTkLabel(self.content_frame, text=f"{label} Command:").pack(pady=(10, 0))
            var = ctk.StringVar(value=self.controller.commands[key])
            entry = ctk.CTkEntry(self.content_frame, textvariable=var, width=300)
            entry.pack(pady=2)
            self.command_vars[key] = var

        ctk.CTkButton(self.content_frame, text="Save", command=self.save_commands).pack(pady=15)

    def save_commands(self):
        for key, var in self.command_vars.items():
            self.controller.commands[key] = var.get().strip()
        self.controller.save_commands()  # <-- Save to file
        self.log("Voice commands updated.")
        ctk.CTkLabel(self.content_frame, text="Commands saved!", text_color="green").pack()

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.stop_event.clear()
            self.status_label.configure(text="Status: Listening")
            self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.listen_thread.start()
            self.log("Listening started.")

    def stop_listening(self):
        self.listening = False
        self.stop_event.set()
        self.status_label.configure(text="Status: Idle")
        self.log("Listening stopped.")
        print("Listening stopped.")

    def listen_loop(self):
        while self.listening and not self.stop_event.is_set():
            text = self.controller.continuous_listen(stop_event=self.stop_event)
            if not self.listening or self.stop_event.is_set():
                break
            if text:
                text = text.strip().lower()
                cmds = self.controller.commands
                if text == cmds["create"]:
                    self.controller.create_notepad()  # prompts for filename
                elif text == cmds["open"]:
                    self.controller.open_notepad()    # prompts for filename
                elif cmds["save"] in text:
                    self.controller.save_notepad()
                elif cmds["close"] in text:
                    self.controller.close_notepad()
                else:
                    self.controller.write_text(text)
                # Update GUI labels if needed
                if hasattr(self, "current_file_label"):
                    if self.controller.current_file_path:
                        self.current_file_label.configure(
                            text=f"Current file: {os.path.basename(self.controller.current_file_path)}"
                        )
                    else:
                        self.current_file_label.configure(text="Current file: None")
                self.last_command_label.configure(text=f"Last command: {text}")
        print("Listen loop exited.")

    def open_folder(self):
        folder = self.controller.script_directory
        os.startfile(folder)

    def view_logs(self):
        LogsDialog(self, self.logs)

    def log(self, message):
        # Only log if log_box exists and is visible
        if hasattr(self, "log_box") and self.log_box.winfo_exists():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.configure(state="disabled")
            self.log_box.see("end")
        self.logs.append(message)

if __name__ == "__main__":
    app = VoiceNotepadApp()
    app.mainloop()