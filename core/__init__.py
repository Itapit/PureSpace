# Import key functions from each module
from .helpers import ensure_directory_exists, is_folder_empty, DirectoryNotFoundError, FileMoveError
from .media_organizer import organize_media_by_date, move_media_duplicates, delete_duplicates_folders, check_ffmpeg_installed
from .cleaner import delete_empty_files, delete_empty_folders, find_large_files, move_unwanted_files

# List of public functions accessible with `from core import *`
__all__ = [
    "ensure_directory_exists",
    "is_folder_empty",
    "DirectoryNotFoundError",
    "FileMoveError",
    "organize_media_by_date",
    "check_ffmpeg_installed",
    "move_media_duplicates",
    "delete_duplicates_folders",
    "delete_empty_files",
    "delete_empty_folders",
    "find_large_files",
    "move_unwanted_files"
]
