import os
import shutil


# Set up directories
DEST_IMAGES = os.path.join(SOURCE_DIR, "Sorted_Images_videos")
UNSORTED_FOLDER = os.path.join(DEST_IMAGES, "Unsorted")
DEST_DUPLICATES = os.path.join(DEST_IMAGES, "duplicates")
DEST_TEMP_FILES = os.path.join(SOURCE_DIR, "Temp_Files")
UNWANTED_FILES_FOLDER = os.path.join(SOURCE_DIR, "Unwanted_Files")

# Hash storage for duplicate detection
hashes = {}



def move_duplicates_by_folder():
    """Scans each date-based folder (`YYYY/MM/`) for duplicate images/videos and moves them to a `duplicates/` folder."""

    for year in os.listdir(DEST_IMAGES):  # Loop through year folders (YYYY)
        year_path = os.path.join(DEST_IMAGES, year)
        if not os.path.isdir(year_path):
            continue  # Skip if not a folder

        for month in os.listdir(year_path):  # Loop through month folders (MM)
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue  # Skip if not a folder

            # ✅ Create a duplicates folder inside `YYYY/MM/`
            duplicates_folder = os.path.join(month_path, "duplicates")
            ensure_directory_exists(duplicates_folder)

            hashes = {}  # Store hashes of files in this folder

            for file in os.listdir(month_path):  # Scan files in `YYYY/MM/`
                file_path = os.path.join(month_path, file)
                file_ext = os.path.splitext(file)[1].lower()

                # ✅ Skip non-media files
                if file_ext not in IMAGE_EXTENSIONS and file_ext not in VIDEO_EXTENSIONS:
                    continue

                # ✅ Skip files inside the `duplicates/` folder
                if os.path.basename(os.path.dirname(file_path)) == "duplicates":
                    continue

                try:
                    file_hash = get_file_hash(file_path)  # Compute hash

                    if file_hash in hashes:
                        # ✅ Duplicate found, move it to `duplicates/`
                        new_file_path = os.path.join(duplicates_folder, file)

                        # ✅ Avoid overwriting by renaming
                        counter = 1
                        while os.path.exists(new_file_path):
                            base_name, ext = os.path.splitext(file)
                            new_file_path = os.path.join(duplicates_folder, f"{base_name}_{counter}{ext}")
                            counter += 1

                        shutil.move(file_path, new_file_path)
                        print(f"📂 Duplicate Moved: {file_path} -> {new_file_path}")

                    else:
                        hashes[file_hash] = file_path  # Store unique file

                except OSError as e:
                    print(f"⚠ Warning: Skipping unreadable file {file_path} - {e}")


def delete_duplicates_folders():
    """Finds and deletes all `duplicates/` folders inside `Sorted_Images_videos/YYYY/MM/`."""
    print("🗑️ Deleting all 'duplicates/' folders...")

    for year in os.listdir(DEST_IMAGES):
        year_path = os.path.join(DEST_IMAGES, year)
        if not os.path.isdir(year_path):
            continue  # Skip non-folders

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue  # Skip non-folders

            duplicates_folder = os.path.join(month_path, "duplicates")
            if os.path.exists(duplicates_folder):
                try:
                    # 🟢 First, delete all files inside the `duplicates` folder.
                    for root, _, files in os.walk(duplicates_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            print(f"🗑️ Deleted: {file_path}")

                    # 🟢 Then, remove the empty `duplicates` folder itself.
                    os.rmdir(duplicates_folder)
                    print(f"✅ Deleted empty folder: {duplicates_folder}")

                except PermissionError:
                    print(f"⚠️ Skipped (Permission Denied): {duplicates_folder}")
                except OSError as e:
                    print(f"⚠️ Failed to delete {duplicates_folder}: {e}")

    print("🚀 Cleanup complete! All duplicate folders have been removed.")

def move_unwanted_files():
    """Moves unwanted files by extension and specific filenames to 'Unwanted_Files'."""
    ensure_directory_exists(UNWANTED_FILES_FOLDER)

    for root, _, files in os.walk(SOURCE_DIR):
        # ✅ Skip system and excluded folders
        if any(root.startswith(os.path.join(SOURCE_DIR, folder)) for folder in EXCLUDED_FOLDERS):
            continue

        for file in files:
            file_lower = file.lower()  # Normalize filename for case-insensitive matching
            file_ext = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)

            # ✅ Check if file is unwanted (by name or extension)
            if file_lower in UNWANTED_FILES or file_ext in UNWANTED_EXTENSIONS:
                new_file_path = os.path.join(UNWANTED_FILES_FOLDER, file)

                # ✅ Avoid overwriting files by appending a number if needed
                counter = 1
                while os.path.exists(new_file_path):
                    base_name, ext = os.path.splitext(file)
                    new_file_path = os.path.join(UNWANTED_FILES_FOLDER, f"{base_name}_{counter}{ext}")
                    counter += 1

                try:
                    shutil.move(file_path, new_file_path)
                    print(f"🚮 Moved: {file_path} -> {new_file_path}")
                except PermissionError:
                    print(f"⚠ Warning: Skipped (Permission Denied) → {file_path}")
                except OSError as e:
                    print(f"⚠ Warning: Could not move {file_path}: {e}")
