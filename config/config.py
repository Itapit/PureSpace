import json
import os

# Paths for configuration files
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "default_config.json")
USER_CONFIG_PATH = os.path.join(CONFIG_DIR, "user_config.json")


# Singleton Metaclass
class SingletonMeta(type):
    """Metaclass to implement the Singleton pattern."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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
            print(f"Warning: Could not load {path}. Using defaults.")
            return {}
    
    def _save_user_config(self):
        """Save the current configuration to user_config.json."""
        try:
            with open(USER_CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error: Failed to save user config - {e}")

    def get(self, key):
        """Retrieve a value from the configuration."""
        return self.config.get(key)
    
    def set(self, **kwargs):
        """Update configuration values and save them."""
        valid_keys = set(self.config.keys())  # Ensure we only update valid keys
        updated_keys = {}

        for key, value in kwargs.items():
            if key in valid_keys:
                self.config[key] = value
                updated_keys[key] = value
            else:
                print(f"Warning: {key} is not a valid config key.")
        if updated_keys:
            self._save_user_config()
            print("Updated settings:", updated_keys)

    def update(self, **kwargs):
        """Update configuration values and save to user_config.json."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"Updated: {key} → {value}")
            else:
                print(f"Warning: Invalid config key - {key}")
        self._save_user_config()

    def show_config(self):
        """Display the current configuration settings."""
        print("Current Configuration:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")


# Singleton Instance (Used across all modules)
config = Config()
