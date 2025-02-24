import os
from core.helpers import ensure_directory_exists, is_excluded_path, safe_move_file
from config.config import config
from PIL import Image, UnidentifiedImageError
from datetime import datetime
import subprocess


def get_image_date(file_path):
    """Extracts image creation date from Exif metadata, otherwise falls back to file creation date."""
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                date_str = exif_data.get(36867)  # "DateTimeOriginal" EXIF tag
                if date_str:
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except (UnidentifiedImageError, AttributeError, KeyError, ValueError):
        pass

    try:
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    except OSError:
        print(f"Warning: Could not access file date for {file_path}")
        return None

def get_video_date(file_path):
    """Extracts video creation date using FFmpeg's `ffprobe`. Falls back to modified date if metadata is missing."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format_tags=creation_time",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        date_str = result.stdout.strip()

        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    except (subprocess.SubprocessError, ValueError):
        pass
    # Fallback: Use last modified date
    try:
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    except OSError:
        print(f"Warning: Could not access file date for {file_path}")
        return None

def organize_media_by_date(dry_run=False, merge_media=True):
    """Organize images and videos into year/month folders. Optionally merge them into separate folders."""
    source_dir = config.get("source_dir")
    image_extensions = config.get("image_extensions")
    video_extensions = config.get("video_extensions")
    excluded_folders = config.get("excluded_folders")

    # Choose destination folders based on merge setting
    base_folder = os.path.join(source_dir, "Sorted_Media")
    media_folder = base_folder if merge_media else None
    image_folder = media_folder if merge_media else os.path.join(base_folder, "Images")
    video_folder = media_folder if merge_media else os.path.join(base_folder, "Videos")

    # Process both images and videos
    for root, _, files in os.walk(source_dir):
        if is_excluded_path(root, excluded_folders):
            continue

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            file_path = os.path.join(root, file)

            # Handle Images
            if file_ext in image_extensions:
                file_date = get_image_date(file_path)
                target_folder = image_folder
            # Handle Videos
            elif file_ext in video_extensions:
                file_date = get_video_date(file_path)
                target_folder = video_folder
            else:
                continue

            # Handle missing metadata
            if not file_date or file_date.year < 1990 or file_date.year > datetime.now().year:
                unsorted_folder = os.path.join(target_folder, "Unsorted")
                ensure_directory_exists(unsorted_folder)
                new_file_path = os.path.join(unsorted_folder, file)

                if dry_run:
                    print(f"[DRY RUN] Would move to Unsorted: {file_path} → {new_file_path}")
                else:
                    safe_move_file(file_path, new_file_path)
                    print(f"[Unsorted] Moved: {file_path} → {new_file_path}")
                continue

            # Organize by Year/Month
            year, month = file_date.strftime("%Y"), file_date.strftime("%m")
            dest_folder = os.path.join(target_folder, year, month)
            ensure_directory_exists(dest_folder)

            # Move the file
            new_file_path = os.path.join(dest_folder, file)
            if dry_run:
                print(f"[DRY RUN] Would move: {file_path} → {new_file_path}")
            else:
                safe_move_file(file_path, new_file_path)
                print(f"Moved: {file_path} → {new_file_path}")
