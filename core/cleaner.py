import os
from core.helpers import ensure_directory_exists, is_folder_empty, bytes_to_mb, is_excluded_path, safe_move_file, validate_source_dir, FileMoveError
from services.services import *
from core.wrappers import operation_wrapper,with_dry_run,walk_directory

@operation_wrapper
@with_dry_run(default=False)
def delete_empty_files(source_dir, dry_run):
    """Delete empty files while skipping excluded directories. Set dry_run=True to simulate the process."""
    excluded_folders = config.get("excluded_folders")

    for root, _, files in walk_directory(source_dir, excluded_folders):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) == 0:
                if dry_run:
                    logger.info(f"[DRY RUN] Would delete empty file: {file_path}")
                else:
                    os.remove(file_path)
                    logger.info(f"Deleted empty file: {file_path}")

@operation_wrapper
@with_dry_run(default=False)
def delete_empty_folders(source_dir, dry_run):
    """Delete empty folders while skipping excluded directories. Set dry_run=True to simulate the process."""
    excluded_folders = config.get("excluded_folders")

    for root, dirs, _ in walk_directory(source_dir, excluded_folders, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if is_excluded_path(folder_path, excluded_folders):
                continue

            if is_folder_empty(folder_path):
                if dry_run:
                    logger.info(f"[DRY RUN] Would delete empty folder: {folder_path}")
                else:
                    os.rmdir(folder_path)
                    logger.info(f"Deleted empty folder: {folder_path}")

@operation_wrapper
def find_large_files(source_dir):
    """Find files larger than the defined size threshold."""
    excluded_folders = config.get("excluded_folders")
    size_threshold_mb = config.get("size_threshold_mb")

    for root, _, files in walk_directory(source_dir, excluded_folders):
        for file in files:
            file_path = os.path.join(root, file)
            size_mb = bytes_to_mb(os.path.getsize(file_path))
            if size_mb > size_threshold_mb:
                logger.info(f"Large file found: {file_path} ({size_mb:.2f} MB)")

@operation_wrapper
@with_dry_run(default=False)
def move_unwanted_files(source_dir, dry_run):
    """Move unwanted files by extension or name to the Unwanted_Files folder."""
    unwanted_extensions = config.get("unwanted_extensions")
    unwanted_files = config.get("unwanted_files")
    excluded_folders = config.get("excluded_folders")
    unwanted_folder = os.path.join(source_dir, "Unwanted_Files")

    ensure_directory_exists(unwanted_folder)

    # Walk through the source directory, skipping excluded folders
    for root, _, files in walk_directory(source_dir, excluded_folders):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            # Check if the file matches unwanted criteria
            if file_ext in unwanted_extensions or file.lower() in unwanted_files:
                destination_path = os.path.join(unwanted_folder, file)

                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {file_path} -> {destination_path}")
                else:
                    safe_move_file(file_path, destination_path)
                    logger.info(f"Moved: {file_path} -> {destination_path}")