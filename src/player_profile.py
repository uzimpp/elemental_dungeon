import os
from config import Config as C

class PlayerProfile:
    """
    Singleton class for managing player profile data across game sessions.
    Uses the Singleton pattern to ensure only one instance exists.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlayerProfile, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._player_name = "Unknown"
    

    def _save_data(self):
        """Save player data to file"""
        try:
            # Create directory if it doesn't exist
            save_dir = os.path.dirname(C.PLAYER_SAVE_FILE)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            with open(C.PLAYER_SAVE_FILE, 'w') as f:
                f.write(f"{self._player_name}\n")
                f.write(f"{self._high_score}\n")
                f.write(f"{self._games_played}\n")
        except Exception as e:
            print(f"Error saving player data: {e}")
    
    @property
    def player_name(self):
        return self._player_name
    
    @player_name.setter
    def player_name(self, name):
        self._player_name = name
        self._save_data()
    
    @property
    def high_score(self):
        return self._high_score
    
    @high_score.setter
    def high_score(self, score):
        if score > self._high_score:
            self._high_score = score
            self._save_data()
    
    @property
    def games_played(self):
        return self._games_played
    
    def increment_games_played(self):
        self._games_played += 1
        self._save_data()
