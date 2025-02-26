import os
from core.helpers import ensure_directory_exists, is_folder_empty, bytes_to_mb, is_excluded_path, safe_move_file
from config.config import config


def delete_empty_files(dry_run=False):
    """Delete empty files while skipping excluded directories. Set dry_run=True to simulate the process."""
    source_dir = config.get("source_dir")
    excluded_folders = config.get("excluded_folders")

    for root, _, files in os.walk(source_dir):
        if is_excluded_path(root, excluded_folders):
            continue

        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) == 0:
                if dry_run:
                    print(f"[DRY RUN] Would delete empty file: {file_path}")
                else:
                    os.remove(file_path)
                    print(f"Deleted empty file: {file_path}")

def delete_empty_folders(dry_run=False):
    """Delete empty folders while skipping excluded directories. Set dry_run=True to simulate the process."""
    source_dir = config.get("source_dir")
    excluded_folders = config.get("excluded_folders")

    for root, dirs, _ in os.walk(source_dir, topdown=False):
        if is_excluded_path(root, excluded_folders):
            continue

        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if is_excluded_path(folder_path, excluded_folders):
                continue

            if is_folder_empty(folder_path):
                if dry_run:
                    print(f"[DRY RUN] Would delete empty folder: {folder_path}")
                else:
                    try:
                        os.rmdir(folder_path)
                        print(f"Deleted empty folder: {folder_path}")
                    except PermissionError:
                        print(f"Warning: Skipped (Permission Denied) → {folder_path}")
                    except OSError as e:
                        print(f"Warning: Could not delete {folder_path}: {e}")

def find_large_files():
    """Find files larger than the defined size threshold."""
    source_dir = config.get("source_dir")
    size_threshold_mb = config.get("size_threshold_mb")
    excluded_folders = config.get("excluded_folders")

    for root, _, files in os.walk(source_dir):
        if is_excluded_path(root, excluded_folders):
                continue

        for file in files:
            file_path = os.path.join(root, file)
            size_mb = bytes_to_mb(os.path.getsize(file_path))
            if size_mb > size_threshold_mb:
                print(f"Large file found: {file_path} ({size_mb:.2f} MB)")

def move_unwanted_files(dry_run=True):
    """Move unwanted files by extension or name to the Unwanted_Files folder."""
    source_dir = config.get("source_dir")
    unwanted_extensions = config.get("unwanted_extensions", [])
    unwanted_files = config.get("unwanted_files", [])
    excluded_folders = config.get("excluded_folders")
    unwanted_folder = os.path.join(source_dir, "Unwanted_Files")

    ensure_directory_exists(unwanted_folder)

    # Walk through the source directory, skipping excluded folders
    for root, _, files in os.walk(source_dir):
        if is_excluded_path(root, excluded_folders):
            continue

        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            # Check if the file matches unwanted criteria
            if file_ext in unwanted_extensions or file.lower() in unwanted_files:
                destination_path = os.path.join(unwanted_folder, file)

                if dry_run:
                    print(f"[DRY RUN] Would move: {file_path} -> {destination_path}")
                else:
                    try:
                        safe_move_file(file_path, destination_path)
                        print(f"Moved: {file_path} -> {destination_path}")
                    except (PermissionError, OSError) as e:
                        print(f"Failed to move {file_path}: {e}")