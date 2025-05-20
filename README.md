# Voice Notepad Automation

A Python desktop application that lets you control Notepad using your voice.  
Built with **CustomTkinter** for the GUI, **SpeechRecognition** for voice input, and **PyAutoGUI** for automating Notepad actions.

---

## Features

- **Voice-controlled Notepad:** Create, open, save, close, and write to Notepad using voice commands.
- **Customizable commands:** Change the trigger phrases for each action.
- **GUI settings:** Adjust sensitivity, theme, default folder, and more.
- **Logs:** View all actions and errors in a log window.
- **Multi-threaded listening:** Voice recognition runs in the background.
- **Portable:** Can be packaged as a `.exe` for easy sharing.

---

## How It Works

1. **User launches the app** (`app_gui.py` or `.exe`).
2. **GUI loads** and initializes a `NotepadController` (from `hcidublicate.py`).
3. **User clicks "Start Listening"**; the app listens for voice commands in a background thread.
4. **Recognized commands** (like "open", "save", etc.) trigger Notepad actions.
5. **Other speech** is typed into Notepad using automation.
6. **Settings and commands** can be customized via the GUI and are saved to JSON files.

---

## Project Structure

```
voice-notepad-automation/
│
├── app_gui.py           # Main GUI application
├── hcidublicate.py      # Notepad controller (backend logic)
├── settings.json        # User settings (auto-created/updated)
├── commands.json        # Custom voice commands (auto-created/updated)
├── requirements.txt     # Python dependencies
└── dist/app_gui.exe     # (After packaging) Standalone executable
```

---

## Class & Function Explanations

### app_gui.py

#### **VoiceNotepadApp (ctk.CTk)**
The main GUI application class.

- **__init__**  
  - Initializes the window, loads settings, creates the main content frame, and shows the home screen.
  - Creates an instance of `NotepadController` (backend logic).

- **show_home**  
  - Builds the home screen: status, buttons (start/stop listening, open folder, settings, controls), log box, and footer.
  - Starts listening automatically on launch.

- **show_settings**  
  - Displays the settings screen:  
    - Sensitivity slider  
    - Default notes folder  
    - Dark mode toggle  
    - Reset buttons  
    - Save button  
    - App version and hotkey info  
  - Loads current settings from file.

- **update_sensitivity**  
  - Updates the controller’s sensitivity in real time when the slider is moved.

- **browse_folder**  
  - Opens a dialog to select a folder for saving notes.

- **toggle_dark_mode**  
  - Switches between dark and light themes.

- **reset_settings**  
  - Resets sensitivity, folder, and theme to defaults.

- **reset_commands**  
  - Resets voice commands to their default phrases and saves them.

- **save_settings**  
  - Saves all settings (sensitivity, folder, theme, autostart) to `settings.json` and updates the controller.

- **load_settings**  
  - Loads settings from `settings.json` (if present) and updates the controller.

- **show_controls**  
  - Lets the user customize the voice command phrases for create, open, save, and close actions.

- **save_commands**  
  - Saves the customized commands to `commands.json` and updates the controller.

- **start_listening**  
  - Starts the background thread for continuous voice recognition.

- **stop_listening**  
  - Stops the listening thread and updates the status.

- **listen_loop**  
  - Runs in a background thread.  
  - Continuously listens for voice input and processes commands:
    - If the recognized text matches a command, triggers the corresponding Notepad action.
    - Otherwise, writes the text into Notepad.
    - Updates GUI labels for status, last command, and current file.

- **open_folder**  
  - Opens the folder where notes are saved.

- **view_logs**  
  - Opens a dialog showing the log history.

- **log**  
  - Appends a message to the log box and internal log list.

---

#### **SettingsDialog (ctk.CTkToplevel)**
- A popup window for settings, similar to `show_settings`.

#### **LogsDialog (ctk.CTkToplevel)**
- A popup window that displays the log history in a read-only textbox.

---

### hcidublicate.py

#### **NotepadController**
Handles all backend logic for Notepad automation and voice command processing.

- **__init__**  
  - Sets up state, loads commands from `commands.json`, and sets up the speech recognizer.

- **load_commands / save_commands**  
  - Loads/saves custom command phrases from/to `commands.json`.

- **speech_to_text**  
  - Listens for a single phrase from the microphone and returns the recognized text using Google Speech Recognition.

- **continuous_listen**  
  - Continuously listens for speech input (in a loop), returning recognized text as soon as it’s heard.

- **get_valid_filename**  
  - Prompts the user (via voice) for a filename and waits until a valid name is spoken.

- **_open_notepad**  
  - Opens Notepad, optionally with a specific file.

- **create_notepad / create_notepad_with_name**  
  - Creates a new text file and opens it in Notepad.

- **open_notepad / open_notepad_with_name**  
  - Opens an existing text file in Notepad.

- **save_notepad**  
  - Simulates Ctrl+S in Notepad to save the current file.

- **close_notepad / close_all_notepads**  
  - Closes Notepad (all instances) using Windows taskkill.

- **write_text**  
  - Pastes the given text into Notepad using the clipboard and PyAutoGUI.

- **main**  
  - (CLI only) Runs the main loop for voice command processing (not used in GUI mode).

---

## Settings & Customization

- **settings.json**  
  - Stores sensitivity, notes folder, theme, and autostart preference.
  - Auto-created/updated by the app.

- **commands.json**  
  - Stores the custom phrases for each voice command.
  - Can be edited via the GUI.

---

## Packaging & Distribution

- Use **PyInstaller** to package the app as a standalone `.exe`:
  ```sh
  pyinstaller --noconfirm --onefile --windowed --add-data "hcidublicate.py;." --add-data "settings.json;." --add-data "commands.json;." app_gui.py
  ```
- Only distribute the `.exe` (and optionally the JSON files for defaults).
- Users do **not** need Python or pip installed.

---

## Troubleshooting

- **Voice not recognized:**  
  - Check microphone selection and sensitivity in settings.
  - Try speaking in short phrases, not single words.
- **Notepad not opening or writing:**  
  - Make sure Notepad is installed and accessible.
  - Ensure the app has permission to control windows and clipboard.
- **Settings not saving/loading:**  
  - Check for write permissions in the app folder.
  - The app will auto-create missing JSON files with defaults.

---

## Dependencies

- `customtkinter` (GUI)
- `SpeechRecognition` (voice input)
- `PyAudio` (microphone access)
- `pyautogui` (keyboard/mouse automation)
- `pyperclip` (clipboard)
- `psutil` (process management)
- `requests` (optional, for updates or web features)
- `darkdetect` (theme detection, optional)

Install all dependencies with:
```sh
pip install -r requirements.txt
```
---

## Example Usage

1. **Launch the app** (`app_gui.exe` or `python app_gui.py`).
2. **Click "Start Listening"**.
3. **Say a command** (e.g., "open", "create a new notepad", "save the notepad", "close notepad").
4. **Dictate text** to write into Notepad.
5. **Customize commands and settings** as needed.

---

## Code Walkthrough (for Presentation)

- **app_gui.py** is the entry point and handles all user interaction.
- **NotepadController** (from `hcidublicate.py`) is the backend for all Notepad and voice logic.
- **Settings and commands** are fully customizable and persist between runs.
- **Logs** provide a full history of actions and errors for transparency and debugging.

---