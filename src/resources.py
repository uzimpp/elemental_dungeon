"""
Resource manager for game resources like audio files, images, etc.
This class ensures resources are loaded only once and stored in memory.
"""
import os
import csv
import pygame
import time
import datetime


class Resources:
    """
    Singleton resources manager for game resources like audio files, images, etc.
    This class ensures resources are loaded only once and stored in memory.
    """
    _instance = None
    
    # Logging levels
    LOG_NONE = 0
    LOG_ERROR = 1
    LOG_WARNING = 2
    LOG_INFO = 3
    LOG_DEBUG = 4

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            # Resource storage dictionaries
            self._resources = {}  # General resources
            self._images = {}     # Image/sprite resources
            self._sounds = {}     # Sound resources
            self._animations = {} # Animation configurations
            self._csv_data = {}   # CSV data
            
            # Base paths
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.asset_path = os.path.join(self.base_path, "assets")
            self.data_path = os.path.join(self.base_path, "data")
            
            # Logging
            self.log_level = self.LOG_INFO  # Default log level
            self.log_file = None
            self.logs = []
            self.max_logs = 1000  # Maximum number of logs to keep in memory
            
            self.initialized = True
            self.log(self.LOG_INFO, f"Initialized (base path: {self.base_path})")
            
    def enable_file_logging(self, log_file=None):
        """Enable logging to a file."""
        if log_file is None:
            log_dir = os.path.join(self.data_path, "logs")
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"resources_{timestamp}.log")
        
        self.log_file = log_file
        self.log(self.LOG_INFO, f"Enabled file logging to: {self.log_file}")
        
    def disable_file_logging(self):
        """Disable logging to a file."""
        if self.log_file:
            self.log(self.LOG_INFO, "Disabled file logging")
            self.log_file = None
            
    def set_log_level(self, level):
        """Set the log level."""
        self.log_level = level
        level_names = {
            self.LOG_NONE: "NONE",
            self.LOG_ERROR: "ERROR",
            self.LOG_WARNING: "WARNING",
            self.LOG_INFO: "INFO",
            self.LOG_DEBUG: "DEBUG"
        }
        self.log(self.LOG_INFO, f"Set log level to: {level_names.get(level, level)}")
        
    def log(self, level, message):
        """Log a message if the level is less than or equal to the current log level."""
        if level <= self.log_level:
            level_names = {
                self.LOG_ERROR: "ERROR",
                self.LOG_WARNING: "WARNING",
                self.LOG_INFO: "INFO",
                self.LOG_DEBUG: "DEBUG"
            }
            level_name = level_names.get(level, "UNKNOWN")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] [{level_name}] [Resources] {message}"
            
            # Print to console
            print(log_message)
            
            # Store in memory
            self.logs.append(log_message)
            if len(self.logs) > self.max_logs:
                self.logs.pop(0)  # Remove oldest log
                
            # Write to file if enabled
            if self.log_file:
                try:
                    with open(self.log_file, "a") as f:
                        f.write(log_message + "\n")
                except Exception as e:
                    print(f"Error writing to log file: {e}")

    def get_path(self, relative_path):
        """Convert a relative path to an absolute path based on the game's root directory"""
        if os.path.isabs(relative_path):
            return relative_path
            
        if relative_path.startswith("assets/"):
            return os.path.join(self.base_path, relative_path)
        elif relative_path.startswith("data/"):
            return os.path.join(self.base_path, relative_path)
        else:
            return os.path.join(self.base_path, relative_path)

    def exists(self, relative_path):
        """Check if a file exists."""
        full_path = self.get_path(relative_path)
        exists = os.path.exists(full_path)
        if not exists:
            self.log(self.LOG_WARNING, f"File not found: {full_path}")
        return exists

    def load_file(self, name, relative_path):
        """Load a file and store it by name. Returns the file path if successful."""
        if name in self._resources:
            self.log(self.LOG_DEBUG, f"Using cached file: {name}")
            return self._resources[name]
            
        full_path = self.get_path(relative_path)
        if not os.path.exists(full_path):
            self.log(self.LOG_ERROR, f"File not found: {full_path}")
            return None
            
        self._resources[name] = full_path
        self.log(self.LOG_INFO, f"Loaded file: {name} -> {full_path}")
        return full_path

    def get_file(self, name):
        """Retrieve a loaded file path by name."""
        return self._resources.get(name, None)

    def load_image(self, name, relative_path):
        """Load and cache an image (sprite sheet) by name."""
        if name in self._images:
            self.log(self.LOG_DEBUG, f"Using cached image: {name}")
            return self._images[name]
            
        full_path = self.get_path(relative_path)
        if not os.path.exists(full_path):
            self.log(self.LOG_ERROR, f"Image file not found: {full_path}")
            return None
            
        try:
            image = pygame.image.load(full_path).convert_alpha()
            self._images[name] = image
            self.log(self.LOG_INFO, f"Loaded image: {name} -> {full_path}")
            return image
        except Exception as e:
            self.log(self.LOG_ERROR, f"Error loading image '{full_path}': {e}")
            return None

    def get_image(self, name):
        """Retrieve a loaded image by name."""
        return self._images.get(name, None)
    
    def load_sound(self, name, relative_path):
        """Load and cache a sound file by name."""
        if name in self._sounds:
            self.log(self.LOG_DEBUG, f"Using cached sound: {name}")
            return self._sounds[name]
            
        full_path = self.get_path(relative_path)
        if not os.path.exists(full_path):
            self.log(self.LOG_ERROR, f"Sound file not found: {full_path}")
            return None
            
        try:
            sound = pygame.mixer.Sound(full_path)
            self._sounds[name] = sound
            self.log(self.LOG_INFO, f"Loaded sound: {name} -> {full_path}")
            return sound
        except Exception as e:
            self.log(self.LOG_ERROR, f"Error loading sound '{full_path}': {e}")
            return None
            
    def get_sound(self, name):
        """Retrieve a loaded sound by name."""
        return self._sounds.get(name, None)
    
    def load_csv(self, name, relative_path):
        """Load a CSV file and parse it into a list of dictionaries."""
        if name in self._csv_data:
            self.log(self.LOG_DEBUG, f"Using cached CSV data: {name}")
            return self._csv_data[name]
            
        full_path = self.get_path(relative_path)
        if not os.path.exists(full_path):
            self.log(self.LOG_ERROR, f"CSV file not found: {full_path}")
            return None
            
        try:
            data = []
            with open(full_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    data.append(row)
                    
            self._csv_data[name] = data
            self.log(self.LOG_INFO, f"Loaded CSV: {name} -> {full_path} ({len(data)} rows)")
            return data
        except Exception as e:
            self.log(self.LOG_ERROR, f"Error loading CSV '{full_path}': {e}")
            return None
            
    def get_csv_data(self, name):
        """Retrieve loaded CSV data by name."""
        return self._csv_data.get(name, None)
        
    def load_animation_config(self, name, config):
        """Store an animation configuration by name."""
        self._animations[name] = config
        self.log(self.LOG_INFO, f"Stored animation config: {name}")
        return config
        
    def get_animation_config(self, name):
        """Retrieve an animation configuration by name."""
        return self._animations.get(name, None)
        
    def load_animation_config_from_file(self, name, relative_path):
        """Load animation configuration from a JSON file."""
        if name in self._animations:
            self.log(self.LOG_DEBUG, f"Using cached animation config: {name}")
            return self._animations[name]
            
        full_path = self.get_path(relative_path)
        if not os.path.exists(full_path):
            self.log(self.LOG_ERROR, f"Animation config file not found: {full_path}")
            return None
            
        try:
            import json
            with open(full_path, 'r') as f:
                config = json.load(f)
                self._animations[name] = config
                self.log(self.LOG_INFO, f"Loaded animation config from file: {name} -> {full_path}")
                return config
        except Exception as e:
            self.log(self.LOG_ERROR, f"Error loading animation config from '{full_path}': {e}")
            return None
            
    def save_animation_config(self, name, relative_path=None):
        """Save animation configuration to a JSON file."""
        if name not in self._animations:
            self.log(self.LOG_ERROR, f"No animation config found with name: {name}")
            return False
            
        config = self._animations[name]
        
        # If no path is provided, use a default path
        if relative_path is None:
            relative_path = f"data/animation_configs/{name}.json"
            
        full_path = self.get_path(relative_path)
        
        # Create directory if it doesn't exist
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except Exception as e:
                self.log(self.LOG_ERROR, f"Error creating directory '{dir_path}': {e}")
                return False
                
        try:
            import json
            with open(full_path, 'w') as f:
                json.dump(config, f, indent=2)
                self.log(self.LOG_INFO, f"Saved animation config: {name} -> {full_path}")
                return True
        except Exception as e:
            self.log(self.LOG_ERROR, f"Error saving animation config to '{full_path}': {e}")
            return False

    def has_image(self, name):
        """Check if an image is already loaded."""
        return name in self._images
        
    def has_sound(self, name):
        """Check if a sound is already loaded."""
        return name in self._sounds
        
    def has_csv_data(self, name):
        """Check if CSV data is already loaded."""
        return name in self._csv_data
        
    def has_animation_config(self, name):
        """Check if an animation configuration is already loaded."""
        return name in self._animations
        
    def clear_resources(self, resource_type=None):
        """Clear resources of a specific type or all resources if type is None."""
        if resource_type is None:
            # Clear all resources
            self._resources.clear()
            self._images.clear()
            self._sounds.clear()
            self._animations.clear()
            self._csv_data.clear()
            self.log(self.LOG_INFO, "Cleared all resources")
        elif resource_type == "images":
            self._images.clear()
            self.log(self.LOG_INFO, "Cleared all images")
        elif resource_type == "sounds":
            self._sounds.clear()
            self.log(self.LOG_INFO, "Cleared all sounds")
        elif resource_type == "animations":
            self._animations.clear()
            self.log(self.LOG_INFO, "Cleared all animation configurations")
        elif resource_type == "csv":
            self._csv_data.clear()
            self.log(self.LOG_INFO, "Cleared all CSV data")
        else:
            self.log(self.LOG_WARNING, f"Unknown resource type: {resource_type}")
            
    def get_stats(self):
        """Get statistics about loaded resources."""
        stats = {
            "images": len(self._images),
            "sounds": len(self._sounds),
            "animations": len(self._animations),
            "csv_data": len(self._csv_data),
            "general": len(self._resources)
        }
        return stats
