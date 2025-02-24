import os
from core.helpers import ensure_directory_exists, is_folder_empty, bytes_to_mb, is_excluded_path
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
