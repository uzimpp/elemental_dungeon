import pygame

class Font:
    """Central font for all game fonts to ensure proper initialization"""
    _instance = None
    _initialized = False
    _fonts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Font, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, font_path, sizes):
        """Initialize fonts after pygame has been initialized"""
        if not pygame.get_init():
            raise RuntimeError("Pygame must be initialized before initializing fonts")
            
        self._initialized = True
        self._font_path = font_path
        
        # Load all fonts at specified sizes
        for name, size in sizes.items():
            self._fonts[name] = pygame.font.Font(font_path, size)
    
    def get_font(self, name):
        """Get a font by name"""
        if not self._initialized:
            raise RuntimeError("Call initialize() first")
            
        if name in self._fonts:
            return self._fonts[name]
        
        # If requesting a numeric size directly
        if isinstance(name, int):
            if name not in self._fonts:
                self._fonts[name] = pygame.font.Font(self._font_path, name)
            return self._fonts[name]
        
        raise ValueError(f"Font '{name}' not found")
