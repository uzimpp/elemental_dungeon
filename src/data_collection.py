"""
Module for collecting and storing game data for analysis and debugging.
"""
import time
import csv
import os
from config import Config as C

class DataCollection:
    """
    Class for collecting data from the game and saving it to a CSV file.
    Provides methods to log game session results and analyze player performance.
    """
    log_path = C.LOG_PATH
    skills_path = C.SKILLS_PATH

    @classmethod
    def log_csv(cls, game_start_time, wave, player_name, player_health, player_deck):
        """
        Log game data to CSV file for analysis.
        
        Args:
            game_start_time (float): When the game session started (time.time())
            wave (int): Wave number reached by the player
            player_name (str): Name of the player
            player_health (float): Final health of the player
            player_deck (list): List of skill objects in player's deck
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            g_time = time.time() - game_start_time
            
            # Make sure the directory exists
            directory = os.path.dirname(cls.log_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convert deck to string representation
            deck_str = "|".join([skill.name for skill in player_deck])

            with open(cls.log_path, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                # Write header if file is empty
                if f.tell() == 0:
                    w.writerow([
                        "timestamp", "player_name", "wave_survived",
                        "game_duration", "final_hp", "deck_composition",
                        "skill1", "skill2", "skill3", "skill4"
                    ])

                # Write data row
                w.writerow([
                    now_str,              # timestamp
                    player_name,          # player_name
                    wave,                 # wave_survived
                    f"{g_time:.2f}",      # game_duration
                    player_health,        # final_hp
                    deck_str,             # deck_composition
                    player_deck[0].name if len(player_deck) > 0 else "",  # skill1
                    player_deck[1].name if len(player_deck) > 1 else "",  # skill2
                    player_deck[2].name if len(player_deck) > 2 else "",  # skill3
                    player_deck[3].name if len(player_deck) > 3 else "",  # skill4
                ])
            return True
        except Exception as e:
            print(f"[DataCollection] ERROR writing to CSV: {e}")
            return False
