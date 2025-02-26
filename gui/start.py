import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import *
from config.config import config


class MediaOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Organizer")
        self.root.geometry("550x450")

        # Top Menu (Settings & Help)
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, pady=5)

        self.settings_button = tk.Button(top_frame, text="⚙ Settings", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=10)

        self.help_button = tk.Button(top_frame, text="❓", command=self.show_help)
        self.help_button.pack(side=tk.LEFT)

        # Title
        tk.Label(root, text="Media Organizer", font=("Arial", 14, "bold")).pack(pady=5)

        # Folder Selection
        self.folder_button = tk.Button(root, text="📂 Choose Folder", command=self.choose_folder, width=20)
        self.folder_button.pack(pady=5)

        self.folder_label = tk.Label(root, text=f"Current Folder: {config.get('source_dir')}", font=("Arial", 10))
        self.folder_label.pack(pady=5)

        # Operation Buttons
        self.create_action_button(
            "Organize Media",
            self.organize_media,
            "Sorts images and videos into year/month folders.",
            ["source_dir", "excluded_folders", "image_extensions", "video_extensions"],
            extra_option_label="Sort All Files"
        )
        self.create_action_button(
            "Move Duplicates",
            self.move_duplicates,
            "Moves duplicate media files to a dedicated folder.",
            ["source_dir", "excluded_folders"],
            extra_option_label="Delete Duplicates"
        )
        self.create_action_button(
            "Clean Empty Files/Folders",
            self.clean_empty,
            "Deletes empty files and folders in the source directory.",
            ["source_dir", "excluded_folders"]
        )
        self.create_action_button(
            "Find Large Files",
            self.find_large_files,
            "Lists all files larger than the defined size threshold.",
            ["source_dir", "excluded_folders", "size_threshold_mb"]
        )

        # Log Output
        tk.Label(root, text="Activity Log:", font=("Arial", 10)).pack(pady=5)
        self.log_output = scrolledtext.ScrolledText(root, width=65, height=10)
        self.log_output.pack(pady=5)
        self.log("Ready to organize your media!\n")

    def create_action_button(self, text, command, description, config_keys, extra_option_label=None):
        """Creates an action button with confirmation prompts and optional checkboxes."""
        frame = tk.Frame(self.root)
        frame.pack(pady=5, fill=tk.X)

        extra_option_var = None
        if extra_option_label:
            extra_option_var = tk.BooleanVar()
            extra_option_checkbox = tk.Checkbutton(frame, text=extra_option_label, variable=extra_option_var)
            extra_option_checkbox.pack(side=tk.LEFT, padx=5)

        btn = tk.Button(frame, text=text, command=lambda: wrapped_command(dry_run_var.get(), extra_option_var.get() if extra_option_label else None), width=30)
        btn.pack(side=tk.LEFT, expand=True)

        dry_run_var = tk.BooleanVar()
        dry_run_checkbox = tk.Checkbutton(frame, text="Dry Run", variable=dry_run_var)
        dry_run_checkbox.pack(side=tk.RIGHT, padx=5)

        def wrapped_command(dry_run, extra_option):
            if self.confirm_action(text, description, config_keys):
                command(dry_run, extra_option)

    def confirm_action(self, action_name, description, config_keys):
        """Prompt user before performing an action, showing only relevant config values."""
        relevant_settings = {key: config.get(key) for key in config_keys if config.get(key) is not None}
        formatted_settings = "\n".join([f"{key}: {value}" for key, value in relevant_settings.items()])

        return messagebox.askyesno(
            "Confirm Action",
            f"{description}\n\nRelevant Config Settings:\n{formatted_settings}\n\nProceed?"
        )

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            config.update(source_dir=folder)
            self.folder_label.config(text=f"Current Folder: {folder}")
            self.log(f"Selected Folder: {folder}")

    def organize_media(self, dry_run, merge_files):
        self.log(f"Organizing media... (Dry Run: {dry_run}, Merge Images and Videos: {merge_files})")
        try:
            organize_media_by_date(dry_run=dry_run, merge_media=merge_files)
            self.log("Media organized successfully!")
        except Exception as e:
            self.log(f"Error: {e}")

    def move_duplicates(self, dry_run, delete_after_move):
        self.log(f"Moving duplicates... (Dry Run: {dry_run}, Delete: {delete_after_move})")
        try:
            move_media_duplicates(dry_run=dry_run)
            self.log("Duplicates moved successfully!")

            if delete_after_move:
                delete_duplicates_folders(dry_run=dry_run)
                self.log("Duplicates deleted successfully!")

        except Exception as e:
            self.log(f"Error: {e}")


    def clean_empty(self, dry_run, _):
        self.log(f"Cleaning empty files/folders... (Dry Run: {dry_run})")
        try:
            delete_empty_files(dry_run=dry_run)
            delete_empty_folders(dry_run=dry_run)
            self.log("Empty files and folders removed!")
        except Exception as e:
            self.log(f"Error: {e}")

    def find_large_files(self, dry_run, _):
        self.log(f"Searching for large files... (Dry Run: {dry_run})")
        try:
            find_large_files()
            self.log("Large file search completed!")
        except Exception as e:
            self.log(f"Error: {e}")

    def log(self, message):
        """Log messages to the GUI output."""
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.yview(tk.END)  # Auto-scroll down

    def open_settings(self):
        """Opens a simple GUI to modify user_config.json."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")

        tk.Label(settings_window, text="Modify Configuration", font=("Arial", 12, "bold")).pack(pady=5)

        config_entries = {}
        for key, value in config.config.items():
            tk.Label(settings_window, text=key).pack()
            entry = tk.Entry(settings_window, width=50)
            entry.insert(0, str(value))
            entry.pack()
            config_entries[key] = entry

        def save_config():
            """Saves new config values using the Config class."""
            new_values = {}
            for key, entry in config_entries.items():
                try:
                    new_values[key] = int(entry.get()) if key == "size_threshold_mb" else entry.get()
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for {key}")
                    return

            config.set(**new_values)  
            messagebox.showinfo("Success", "Configuration updated successfully!")

        save_button = tk.Button(settings_window, text="Save", command=save_config)
        save_button.pack(pady=10)

    def show_help(self):
        """Displays recommendations for using the program."""
        help_text = """
        📌 Recommended Usage:
        1️⃣ First, select the source folder where your media is stored.
        2️⃣ Use 'Organize Media' to sort files into year/month folders.
        3️⃣ Run 'Remove Duplicates' to clean up repeated files.
        4️⃣ Use 'Clean Empty Files/Folders' to remove unnecessary items.
        5️⃣ Run 'Find Large Files' to identify files over your size threshold.

        🛠️ Best Practices:
        - Avoid selecting system folders.
        - Check the 'Settings' menu to adjust configurations.
        - Run the program in 'dry_run' mode first to preview changes.
        """
        messagebox.showinfo("How to Use", help_text)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MediaOrganizerApp(root)
    root.mainloop()