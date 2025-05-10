import time
import csv
from config import LOG_PATH, SKILLS_PATH

class DataCollection:
    """
    Class for collecting data from the game and saving it to a CSV file.
    """
    log_path = LOG_PATH
    skills_path = SKILLS_PATH

    @classmethod
    def log_csv(cls, game_start_time, wave, player_name, player_health, player_deck):
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        g_time = time.time() - game_start_time

        # Convert deck to string representation
        deck_str = "|".join([skill.name for skill in player_deck])

        with open(cls.log_path, "a", newline="") as f:
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
                player_deck[0].name,  # skill1
                player_deck[1].name,  # skill2
                player_deck[2].name,  # skill3
                player_deck[3].name,  # skill4
            ])

