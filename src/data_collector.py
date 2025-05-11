import csv
import os
from config import Config as C


class DataCollector:
    """Handles data collection for the game, logging to CSV files."""

    current_play_id = None

    @staticmethod
    def _ensure_data_dir_exists():
        """Ensures the data directory for CSV files exists."""
        log_dir = os.path.dirname(C.GAMES_LOG_PATH)
        waves_dir = os.path.dirname(C.WAVES_LOG_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if waves_dir and waves_dir != log_dir and not os.path.exists(waves_dir):
            os.makedirs(waves_dir)

    @staticmethod
    def _get_next_play_id():
        """Determines the next Play_ID by reading the last ID from log.csv."""
        DataCollector._ensure_data_dir_exists()
        max_id_val = 0
        found_valid_id = False
        try:
            with open(C.GAMES_LOG_PATH, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header

                for row in reader:
                    # Check if row is not empty and has a first element
                    if row and len(row) > 0 and row[0]:
                        try:
                            current_id_val = int(row[0])
                            if current_id_val > max_id_val:
                                max_id_val = current_id_val
                            found_valid_id = True
                        except ValueError:
                            # First column is not a valid integer, silently skip for ID purposes
                            # You could add a print statement here for debugging if needed:
                            # print(f"Warning: Skipping row with non-integer Play_ID '{row[0]}' in {LOG_GAME_CSV}.")
                            pass

            if found_valid_id:
                return f"{max_id_val + 1:04d}"
            # No valid IDs found after header (or file only had header/was empty after skipping header)
            else:
                return "0001"

        except FileNotFoundError:
            return "0001"  # File doesn't exist, start with 0001
        except Exception as e:
            print(f"Error processing {C.GAMES_LOG_PATH} for Play_ID: {e}")
            return "0001"  # Fallback in case of other errors

    @staticmethod
    def initialize_csvs():
        """Initializes CSV files with headers if they don't exist or are empty."""
        DataCollector._ensure_data_dir_exists()
        DataCollector.current_play_id = DataCollector._get_next_play_id()

        # Initialize log.csv
        try:
            needs_header_log = not os.path.exists(
                C.GAMES_LOG_PATH) or os.path.getsize(C.GAMES_LOG_PATH) == 0
            with open(C.GAMES_LOG_PATH, 'a', newline='') as f_log:
                writer_log = csv.writer(f_log)
                if needs_header_log:
                    writer_log.writerow([
                        "Play_ID", "name", "waves_reached",
                        "skill1", "skill2", "skill3", "skill4",
                        "Time_survived_seconds"
                    ])
        except Exception as e:
            print(f"Error initializing {C.GAMES_LOG_PATH}: {e}")

        # Initialize waves.csv
        try:
            needs_header_waves = not os.path.exists(
                C.WAVES_LOG_PATH) or os.path.getsize(C.WAVES_LOG_PATH) == 0
            with open(C.WAVES_LOG_PATH, 'a', newline='') as f_waves:
                writer_waves = csv.writer(f_waves)
                if needs_header_waves:
                    writer_waves.writerow([
                        "Play_ID", "name", "wave", "hp_end_wave", "stamina_end_wave",
                        "skill1_freq", "skill2_freq", "skill3_freq", "skill4_freq",
                        "time_per_wave_sec", "spawned_enemies", "enemies_left"
                    ])
        except Exception as e:
            print(f"Error initializing {C.WAVES_LOG_PATH}: {e}")

        print(
            f"DataCollector initialized. Current Play_ID: {DataCollector.current_play_id}")

    @staticmethod
    def log_game_session_data(player_name, waves_reached, player_deck_skills, game_duration_seconds):
        """Logs data for a completed game session to log.csv."""
        if DataCollector.current_play_id is None:
            print("Error: DataCollector not initialized. Call initialize_csvs() first.")
            return

        DataCollector._ensure_data_dir_exists()
        try:
            with open(C.GAMES_LOG_PATH, 'a', newline='') as f:
                writer = csv.writer(f)
                skills = [
                    skill.name if skill else "" for skill in player_deck_skills]
                # Ensure 4 skills are logged, padding with empty strings if necessary
                while len(skills) < 4:
                    skills.append("")

                writer.writerow([
                    DataCollector.current_play_id,
                    player_name,
                    waves_reached,
                    skills[0], skills[1], skills[2], skills[3],  # skill1-4
                    f"{game_duration_seconds:.2f}"
                ])
        except Exception as e:
            print(f"Error logging game session data to {C.GAMES_LOG_PATH}: {e}")

    @staticmethod
    def log_wave_end_data(player_name, wave_number, player_hp, player_stamina,
                          skill_frequencies, wave_duration_seconds,
                          spawned_enemies_count, enemies_left_count, player_deck_skills):
        """Logs data at the end of each wave to waves.csv."""
        if DataCollector.current_play_id is None:
            print("Error: DataCollector not initialized. Call initialize_csvs() first.")
            return

        DataCollector._ensure_data_dir_exists()
        try:
            with open(C.WAVES_LOG_PATH, 'a', newline='') as f:
                writer = csv.writer(f)

                # Get skill names from deck, match with frequencies
                # Assuming player_deck_skills is a list of Skill objects
                skill_names_in_deck = [
                    skill.name if skill else "" for skill in player_deck_skills]
                # Pad with empty names if less than 4 skills
                while len(skill_names_in_deck) < 4:
                    skill_names_in_deck.append("")

                freqs = []
                for skill_name in skill_names_in_deck:
                    freqs.append(skill_frequencies.get(skill_name, 0))

                # Ensure we have 4 frequency values, even if some skills weren't used or deck has < 4
                while len(freqs) < 4:
                    freqs.append(0)

                writer.writerow([
                    DataCollector.current_play_id,
                    player_name,
                    wave_number,
                    player_hp,
                    player_stamina,
                    # skill1-4 frequencies
                    freqs[0], freqs[1], freqs[2], freqs[3],
                    f"{wave_duration_seconds:.2f}",
                    spawned_enemies_count,
                    enemies_left_count
                ])
        except Exception as e:
            print(f"Error logging wave data to {C.WAVES_LOG_PATH}: {e}")

