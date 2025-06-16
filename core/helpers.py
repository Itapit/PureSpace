import os
import shutil
import hashlib

def ensure_directory_exists(directory):
    """Ensure that the given directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)

def get_file_hash(file_path, algorithm="sha256"):
    """Generate a hash for a given file using the specified algorithm (default: SHA256)."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def is_folder_empty(folder_path):
    """Check if a folder is empty."""
    return not os.listdir(folder_path)


class FileMoveError(Exception):
    """Custom exception for file movement failures."""
    pass

def safe_move_file(src, dest):
    """Move a file to the destination, avoiding overwrites by appending a counter."""
    base, ext = os.path.splitext(dest)
    counter = 1
    while os.path.exists(dest):
        dest = f"{base}_{counter}{ext}"
        counter += 1
    try:
        shutil.move(src, dest)
        return dest
    except Exception as e:
        raise FileMoveError(f"Failed to move {src} to {dest}: {e}")


def bytes_to_mb(size_in_bytes):
    """Convert bytes to megabytes (MB)."""
    return size_in_bytes / (1024 * 1024)

def is_excluded_path(path, excluded_folders):
    """Check if a path should be excluded based on defined folders."""
    return any(os.path.commonpath([path, os.path.abspath(folder)]) == os.path.abspath(folder) for folder in excluded_folders)

class DirectoryNotFoundError(Exception):
    """Custom exception for when the source directory is missing."""
    pass

def validate_source_dir(source_dir):
    """Check if the source directory exists and is accessible."""
    
    if not source_dir or not os.path.exists(source_dir):
        raise DirectoryNotFoundError(f"Source directory does not exist: {source_dir}")

    return True

def safe_create_directory(parent_path, folder_name):
    """
    Create a new folder under parent_path with folder_name.
    If a folder with the name exists, append a counter suffix (e.g., folder_1, folder_2, ...).

    Returns the Path to the created directory.
    """
    base_path = parent_path / folder_name
    candidate = base_path
    counter = 1

    while candidate.exists():
        candidate = parent_path / f"{folder_name}_{counter}"
        counter += 1

    os.makedirs(candidate)
    return candidate

def get_nonconflicting_path(path):
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{base}_{counter}{ext}"
        counter += 1
    return path
