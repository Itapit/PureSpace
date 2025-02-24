from config.config import config

# Display current config
config.show_config()

# Update a value (this will update user_config.json)
config.update(source_dir="E:/Backup", size_threshold_mb=300)

# Access a specific value
print(f"Source Directory: {config.get('source_dir')}")
print(f"Size Threshold: {config.get('size_threshold_mb')} MB")
