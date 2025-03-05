import os
from core.helpers import ensure_directory_exists, is_excluded_path, safe_move_file, get_file_hash, validate_source_dir
from core.wrappers import operation_wrapper,with_dry_run,walk_directory
from services.services import config
from services.services import logger
from PIL import Image, UnidentifiedImageError
from datetime import datetime
import subprocess
import shutil


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
        logger.warning(f"Warning: Could not access file date for {file_path}")
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
        logger.warning(f"Warning: Could not access file date for {file_path}")
        return None

def check_ffmpeg_installed():
    """Check if FFmpeg is installed on the system."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logger.info("FFmpeg is installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("FFmpeg is not installed. Please install FFmpeg to process videos.")
        return False

@operation_wrapper
@with_dry_run(default=False)
def organize_media_by_date(source_dir, dry_run, merge_media=True):
    """Organize images and videos into year/month folders. Optionally merge them into separate folders."""
    image_extensions = config.get("image_extensions")
    video_extensions = config.get("video_extensions")
    excluded_folders = config.get("excluded_folders")

    # Choose destination folders based on merge setting
    base_folder = os.path.join(source_dir, "Sorted_Media")
    media_folder = base_folder if merge_media else None
    image_folder = media_folder if merge_media else os.path.join(base_folder, "Images")
    video_folder = media_folder if merge_media else os.path.join(base_folder, "Videos")

    # Process both images and videos
    for root, _, files in walk_directory(source_dir, excluded_folders):
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
                    logger.info(f"[DRY RUN] Would move to Unsorted: {file_path} → {new_file_path}")
                else:
                    safe_move_file(file_path, new_file_path)
                    logger.info(f"[Unsorted] Moved: {file_path} → {new_file_path}")
                continue

            # Organize by Year/Month
            year, month = file_date.strftime("%Y"), file_date.strftime("%m")
            dest_folder = os.path.join(target_folder, year, month)
            ensure_directory_exists(dest_folder)

            # Move the file
            new_file_path = os.path.join(dest_folder, file)
            if dry_run:
                logger.info(f"[DRY RUN] Would move: {file_path} → {new_file_path}")
            else:
                safe_move_file(file_path, new_file_path)
                logger.info(f"Moved: {file_path} → {new_file_path}")

@operation_wrapper
@with_dry_run(default=False)
def move_media_duplicates(source_dir, dry_run):
    """Move duplicate media files (images/videos) within each month folder under Sorted_Media."""
    sorted_media_dir = os.path.join(source_dir, "Sorted_Media")
    excluded_folders = config.get("excluded_folders")
    media_extensions = config.get("image_extensions") + config.get("video_extensions")

    ensure_directory_exists(sorted_media_dir)

    # Walk through each year and month folder
    for year in os.listdir(sorted_media_dir):
        year_path = os.path.join(sorted_media_dir, year)
        if not os.path.isdir(year_path):
            continue

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path) or is_excluded_path(month_path, excluded_folders):
                continue

            logger.info(f"Scanning for duplicates in: {month_path}")
            file_hashes = {}  # Reset hashes for each month
            duplicates_folder = os.path.join(month_path, "Duplicates")
            ensure_directory_exists(duplicates_folder)

            # Scan all files in the current month folder
            for file in os.listdir(month_path):
                file_path = os.path.join(month_path, file)
                if not os.path.isfile(file_path):
                    continue

                # Check if it's a media file
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in media_extensions:
                    continue

                # Generate hash and detect duplicates
                file_hash = get_file_hash(file_path)
                if file_hash in file_hashes:
                    duplicate_path = os.path.join(duplicates_folder, file)
                    
                    # Avoid overwriting duplicates
                    counter = 1
                    while os.path.exists(duplicate_path):
                        base, ext = os.path.splitext(file)
                        duplicate_path = os.path.join(duplicates_folder, f"{base}_{counter}{ext}")
                        counter += 1

                    if dry_run:
                        logger.info(f"[DRY RUN] Would move duplicate: {file_path} → {duplicate_path}")
                    else:
                        safe_move_file(file_path, duplicate_path)
                        logger.info(f"Moved duplicate: {file_path} → {duplicate_path}")
                else:
                    file_hashes[file_hash] = file_path 

@operation_wrapper
@with_dry_run(default=False)
def delete_duplicates_folders(source_dir, dry_run):
    """Delete 'Duplicates' folders under Sorted_Media, including all contents."""
    sorted_media_dir = os.path.join(source_dir, "Sorted_Media")
    excluded_folders = config.get("excluded_folders")

    ensure_directory_exists(sorted_media_dir)

    # Walk through each year and month folder in Sorted_Media
    for year in os.listdir(sorted_media_dir):
        year_path = os.path.join(sorted_media_dir, year)
        if not os.path.isdir(year_path):
            continue

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path) or is_excluded_path(month_path, excluded_folders):
                continue

            duplicates_folder = os.path.join(month_path, "Duplicates")
            if os.path.exists(duplicates_folder):
                if dry_run:
                    logger.info(f"[DRY RUN] Would delete folder: {duplicates_folder}")
                else:
                    shutil.rmtree(duplicates_folder)
                    logger.info(f"Deleted folder: {duplicates_folder}")