# 📂 PureSpace  
### A Powerful Tool to Clean, Sort, and Organize Your Backup Drive

---

## 🗨️ Why I Built This

After sitting on an **old family backup hard drive** for over 20 years, I finally decided to **sort and clean it up**. What I found was a complete mess — **tons of duplicates, old operating system files, useless leftovers, and more**.

By the end of this process, I **shrunk the drive from 700GB down to only 270GB**, with everything neatly sorted into organized folders.

To speed up the process, I first **copied everything to an SSD**, which made scanning and sorting much faster.

This project was written over just a few days, so there are probably **some bugs and rough edges**. This is a **powerful tool**, so **you need to know what you’re doing** — I take no responsibility if things go wrong!

---

## 📜 Project Overview

**PureSpace** is a desktop application built using Python and Tkinter, designed to help users easily manage their media files (images and videos). It automates the process of sorting files into folders by date, detecting and removing duplicates, and cleaning unwanted files from a chosen directory.

---

## 📁 Project Structure

```text
.
├── gui
│   └── app.py               # Main application GUI (Tkinter)
├── core
│   ├── __init__.py           # Core module exports
│   ├── cleaner.py            # Cleaning operations (empty files, unwanted files)
│   ├── helpers.py             # Utility functions
│   └── media_organizer.py     # Main media sorting and duplicate detection logic
├── services
│   ├── __init__.py            # Service imports
│   ├── services.py            # Configuration and logging (Singleton)
│   ├── default_config.json    # Default settings for file handling
│   └── app.log
└── README.md
```
---

## ✨ Features
Sort images and videos into year/month folders automatically.

Detect and move duplicate files to a dedicated folder.

Find and delete empty files/folders.

Identify and list large files over a size threshold.

Move unwanted files (based on extensions/names) into a cleanup folder.

Fully configurable via Settings in the app.

---

## 🖥️ Technologies Used
Python 3.x

Tkinter (GUI)

Pillow (Image metadata handling)

FFmpeg (Video metadata extraction)

Logging (via Python logging module)

JSON (for configuration)


---
## ⚙️ Installation and setup
Step 1: Clone the Repository
```bash
git clone https://github.com/Itapit/PureSpace.git
cd PureSpace
```
Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
Step 4: Ensure FFmpeg is Installed

Download FFmpeg

Add FFmpeg to your system PATH so the app can find it.

#### ▶️ Running the Application
```bash
python gui/app.py
```

---

## ⚡ Configuration
All settings (folder exclusions, file types, size limits) are stored in:

services/default_config.json (initial defaults)

services/user_config.json (optional user overrides, saved via the GUI Settings window)

---

📊 Example Folder Structure After Sorting
```text
D:/
├── Sorted_Media/
│   ├── 2023/
│   │   ├── 01/  # January
│   │   ├── 02/  # February
│   │   └── ...
│   └── Duplicates/
└── Unwanted_Files/
```

---

## 📌 Recommended Workflow
1️⃣ Select a folder using the Choose Folder button.

2️⃣ Open Settings and customize the file types and rules.

3️⃣ Use the Dry Run option to preview changes before applying.

4️⃣ Run each action (Organize, Clean, etc.) and monitor progress in the log window.


---

## ❗ Important Notes
Avoid selecting system folders like C:\Windows.

FFmpeg is required to read video metadata.

If files lack metadata, they are moved to an Unsorted folder.

I strongly recommend enabling **"View Hidden Files/Folders"** in your file explorer, and adding any **system folders** (like `$RECYCLE.BIN`, `System Volume Information`, etc.) to the excluded folders list in the **Settings**.

---

## Contributing
Feel free to fork this repository and submit a pull request with any improvements!

---

## Contact
For questions or contributions, reach out at ItamarDavid90@gmail.com.

