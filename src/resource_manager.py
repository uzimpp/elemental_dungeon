import pygame
import csv # Import csv for reading skills
import os
from config import *

class ResourceManager:
    """Singleton class for managing game resources"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Resource storage (private attributes)
        self.__resources = {
            "images": {},
            "sprites": {},
            "skills": {},
            "sprite_sheets": {},
            "map": {}
        }
        
        # Ensure directories exist
        self._ensure_directories()

        # if not pygame.mixer.get_init():
        #     pygame.mixer.init()
        # if not pygame.font.get_init():
        #     pygame.font.init()
    
    # Properties for accessing resources
    @property
    def images(self):
        return self._images
    
    @property
    def sprites(self):
        return self._sprites
    
    @property
    def skills(self):
        return self._skills
    
    @property
    def sprite_sheets(self):
        return self._sprite_sheets
    
    @property
    def map_data(self):
        return self._map_data
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        src_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(src_dir)

        # Set correct absolute paths to resource directories
        self.img_dir = os.path.join(project_dir, "assets", "images") # Corrected path
        self.sound_dir = os.path.join(project_dir, "assets", "sounds")
        self.music_dir = os.path.join(project_dir, "assets", "music")
        self.font_dir = os.path.join(project_dir, "assets", "fonts")
        self.data_dir = os.path.join(project_dir, "data") # Corrected path name and target

        print(f"Resource directories set up:")
        print(f"Images: {self.img_dir}")
        print(f"Data: {self.data_dir}")
        # Add prints for sound, music, font if needed
    
    @staticmethod
    def load_resource(file_path, resource_type):
        """
        Static method to load resources by type
        
        Args:
            file_path: Path to the resource file
            resource_type: Type of resource ('image' or 'csv')
            
        Returns:
            The loaded resource
        """
        print(f"Loading {resource_type} from: {file_path}")
        
        try:
            # Load based on resource type
            if resource_type == 'image':
                return pygame.image.load(file_path).convert_alpha()
            elif resource_type == 'csv':
                data = []
                with open(file_path, 'r', newline='') as file:
                    reader = csv.reader(file)
                    headers = next(reader)  # Read headers
                    for row in reader:
                        if not row:  # Skip empty rows
                            continue
                        # Create a dictionary for each row using headers as keys
                        row_dict = {headers[i]: value for i, value in enumerate(row) if i < len(headers)}
                        data.append(row_dict)
                return data
            else:
                raise ValueError(f"Unsupported resource type: {resource_type}")
                
        except Exception as e:
            raise Exception(f"Failed to load {resource_type} from {file_path}: {str(e)}")
    
    def load(self, resource_type, name, file_name):
        """
        Generic method to load any resource type and store it in the appropriate dictionary
        
        Args:
            resource_type: Type of resource ('image', 'sprite', 'csv')
            name: The name/key to store the resource under
            file_name: The file name to load from (relative to appropriate directory)
            
        Returns:
            The loaded resource
        """
        # Determine which resource collection to use based on type
        collections = {
            'image': self._images,
            'sprite': self._sprite_sheets,
            'csv': self._map_data
        }
        
        if resource_type not in collections:
            raise ValueError(f"Unsupported resource type: {resource_type}")
            
        collection = collections[resource_type]
        
        # Return cached resource if already loaded
        if name in collection:
            return collection[name]
        
        # Determine base directory for resource type
        directories = {
            'image': self.img_dir,
            'sprite': self.img_dir,
            'csv': self.data_dir
        }
        
        base_dir = directories[resource_type]
        file_path = os.path.join(base_dir, file_name)
        
        try:
            # For sprite sheets, we treat them as images
            actual_type = 'image' if resource_type == 'sprite' else resource_type
            
            # Use the static method to load the resource
            resource = ResourceManager.load_resource(file_path, actual_type)
            
            # Store in appropriate collection
            collection[name] = resource
            return resource
        except Exception as e:
            raise Exception(f"Failed to load {resource_type} '{name}' from {file_path}: {str(e)}")
    
    # === Image Management ===
    def load_image(self, name, file_name):
        """Load an image into the images dictionary"""
        return self.load('image', name, file_name)
    
    def get_image(self, name):
        """Get a previously loaded image"""
        return self._images.get(name)

    
    def get_sprite_sheet(self, name):
        """Get a previously loaded sprite sheet"""
        return self._sprite_sheets.get(name)
    
    def extract_sprite(self, sheet_name, x, y, width, height):
        """Extract a sprite from a sprite sheet"""
        sheet = self.get_sprite_sheet(sheet_name)
        if not sheet:
            return None
        
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(sheet, (0, 0), (x, y, width, height))
        return sprite
    
    def load_csv_data(self, name, file_name):
        """Load CSV data into the map_data dictionary"""
        return self.load('csv', name, file_name)

    # === Resource Preloading ===
    def preload_resources(self):
        """Preload common game resources"""
        print("Preloading resources...")
        
        # Load sprite sheets (Pass only filename)
        self.load('sprite', 'player_sheet', 'player_sheet.png')
        self.load('sprite', 'enemy_sheet', 'enemy_sheet.png')
        self.load('sprite', 'slime_sheet', 'slime_sheet.png')

        self.load('csv', 'skills', 'skills.csv')
    
    # === Resource Cleanup ===
    def clear_data(self, resource_type=None):
        """Clear resource caches to free memory"""
        if resource_type is None or resource_type == "images":
            self._images.clear()
        
        if resource_type is None or resource_type == "sprite_sheets":
            self._sprite_sheets.clear()
        
        if resource_type is None or resource_type == "map_data":
            self._map_data.clear()