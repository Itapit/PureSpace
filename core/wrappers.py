from functools import wraps
import os
from services.services import logger, config
from core.helpers import validate_source_dir, DirectoryNotFoundError, FileMoveError, is_excluded_path


def get_source_dir():
    source_dir = config.get("source_dir")
    validate_source_dir(source_dir)
    return source_dir

def log_operation(func_name, stage):
    if stage == "start":
        logger.info(f"Starting {func_name}...")
    elif stage == "end":
        logger.info(f"Completed {func_name}.")

def handle_errors(func_name, func):
    try:
        return func()
    except DirectoryNotFoundError as e:
        logger.error(f"[{func_name}] Directory error: {e}")
        raise
    except PermissionError:
        logger.warning(f"Warning: Skipped (Permission Denied)")
    except FileMoveError as e:
        logger.warning(f"Failed to move file: {e}")
    except OSError as e:
        logger.warning(f"Warning: Could not delete: {e}")
    except Exception as e:
        logger.exception(f"[{func_name}] Unexpected error: {e}")
        raise

def walk_directory(source_dir, excluded_folders, topdown=True):
    for root, dirs, files in os.walk(source_dir, topdown=topdown):
        if is_excluded_path(root, excluded_folders):
            continue
        yield root, dirs, files


def operation_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__

        log_operation(func_name, "start")
        def logic():
            source_dir = get_source_dir()  
            return func(source_dir, *args, **kwargs)
        result = handle_errors(func_name, logic)
        log_operation(func_name, "end")

        return result
    return wrapper

def with_dry_run(default=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "dry_run" not in kwargs:
                kwargs["dry_run"] = default
            if kwargs["dry_run"]:
                logger.info(f"{func.__name__} running in DRY RUN mode.")
            return func(*args, **kwargs)
        return wrapper
    return decorator