import json
import os
import logging

# Paths for configuration files
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "default_config.json")
USER_CONFIG_PATH = os.path.join(CONFIG_DIR, "user_config.json")
# Paths for logger
LOG_FILE_PATH = os.path.join(CONFIG_DIR, "app.log")

# Singleton Metaclass
class SingletonMeta(type):
    """Metaclass to implement the Singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    """Centralized logger using Singleton pattern."""
    
    def __init__(self):
        self.logger = logging.getLogger("MediaOrganizer")
        if not self.logger.hasHandlers():
            self.logger.setLevel(logging.DEBUG)
            
            # File Handler
            file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_format)

            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter("%(levelname)s: %(message)s")
            console_handler.setFormatter(console_format)

            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def debug(self, message):
        self.logger.debug(message)


# Config Class using Singleton Metaclass
class Config(metaclass=SingletonMeta):
    """Configuration class to manage app settings with Singleton behavior."""

    def __init__(self):
        """Initialize configuration by loading default and user configs."""
        self.config = self._load_json(DEFAULT_CONFIG_PATH)  # Load defaults
        user_config = self._load_json(USER_CONFIG_PATH)     # Load user preferences
        if user_config:
            self.config.update(user_config)

    def _load_json(self, path):
        """Load JSON file and return its content as a dictionary."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Warning: Could not load {path}. Using defaults.")
            return {}
    
    def _save_user_config(self):
        """Save the current configuration to user_config.json."""
        try:
            with open(USER_CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.warning(f"Error: Failed to save user config - {e}")

    def get(self, key):
        """Retrieve a value from the configuration."""
        return self.config.get(key)
    
    def update(self, **kwargs):
        """Update configuration values and save them, ensuring valid keys."""
        valid_keys = set(self.config.keys())
        updated_keys = {}

        for key, value in kwargs.items():
            if key not in valid_keys:
                logger.warning(f"Warning: {key} is not a valid config key.")
                continue 

            self.config[key] = value
            updated_keys[key] = value

        if updated_keys:
            self._save_user_config()
            logger.info(f"Updated settings: {updated_keys}")

    def show_config(self):
        """Display the current configuration settings."""
        logger.info("Current Configuration:")
        for key, value in self.config.items():
            logger.info(f"  {key}: {value}")


# Singleton Instance (Used across all modules)
logger = Logger()
config = Config()