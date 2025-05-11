import csv
import time
import os
from config import Config as C

class DataCollection:
    """Handles data collection for the game in"""

    @staticmethod
    def log_csv(game, wave):
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        g_time = time.time() - game.game_start_time

        # Convert deck to string representation
        deck_str = "|".join([skill.name for skill in game.player.deck.skills])

        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.dirname(C.LOG_FILENAME)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            with open(C.LOG_FILENAME, "a", newline="") as f:
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
                    now_str,                    # timestamp
                    game.player_name,          # player_name
                    wave,                      # wave_survived
                    f"{g_time:.2f}",          # game_duration
                    game.player.health,        # final_hp
                    deck_str,                  # deck_composition
                    game.player.deck.skills[0].name,  # skill1
                    game.player.deck.skills[1].name,  # skill2
                    game.player.deck.skills[2].name,  # skill3
                    game.player.deck.skills[3].name,  # skill4
                ])
        except Exception as e:
            print(f"Error logging game data: {e}")
