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
        print(f"Error moving {src} to {dest}: {e}")
        return None

def bytes_to_mb(size_in_bytes):
    """Convert bytes to megabytes (MB)."""
    return size_in_bytes / (1024 * 1024)

def is_excluded_path(path, excluded_folders):
    """Check if a path should be excluded based on defined folders."""
    return any(folder in path for folder in excluded_folders)