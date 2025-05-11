from matplotlib.figure import Figure
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import pandas as pd
import threading
import tkinter as tk
from tkinter import ttk
import platform
import tempfile
import sys
import shutil
import multiprocessing
from functools import partial
from config import Config as C
# Ensure Matplotlib TkAgg backend is explicitly imported for main thread/non-macOS use
import matplotlib
matplotlib.use('TkAgg')
# Note: plt, sns, np are used within visualization classes,
# so they are fine as top-level if Tkinter runs in a thread.
# For macOS subprocess, they must be re-imported there.

# Global variables for tracking
tk_stats_thread = None
tk_window_closed = False
tk_subprocess = None
tk_process = None
IS_MACOS = platform.system() == 'Darwin'


def _get_file_path(configured_path):
    """Tries to find a file based on its configured path, returning its absolute path if found."""
    # 1. Try the absolute path of the configured_path directly
    abs_configured_path = os.path.abspath(configured_path)
    if os.path.exists(abs_configured_path):
        return abs_configured_path

    # 2. If configured_path is relative (e.g., "data/log.csv"),
    #    try it relative to the script's parent directory (project root).
    if not os.path.isabs(configured_path):
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        path_relative_to_project_root = os.path.abspath(
            os.path.join(current_script_dir, '..', configured_path)
        )
        if os.path.exists(path_relative_to_project_root):
            return path_relative_to_project_root

        # 3. Also try relative to current working directory as a fallback for relative paths
        # os.path.abspath resolves against CWD for relative paths
        path_relative_to_cwd = os.path.abspath(configured_path)
        if os.path.exists(path_relative_to_cwd) and path_relative_to_cwd != abs_configured_path:
            return path_relative_to_cwd

    print(f"Could not find {configured_path} at expected locations.")
    return None


class Visualization:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)

    def update(self, game_df, waves_df):
        pass

# 1. Summary Statistics Table


class SummaryStatsVisualization(Visualization):
    def __init__(self, parent):
        super().__init__(parent)

        # Header
        tk.Label(self.frame, text=C.VISUALIZE_NAME,
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        # Create stats table
        self.stats_table = ttk.Treeview(self.frame, columns=(
            "Statistic", "Waves Reached", "Game Duration (s)"), show="headings")
        self.stats_table.heading("Statistic", text="Statistic")
        self.stats_table.heading("Waves Reached", text="Waves Reached")
        self.stats_table.heading("Game Duration (s)", text="Game Duration (s)")
        self.stats_table.column("Statistic", anchor="w", width=100)
        self.stats_table.column("Waves Reached", anchor="center", width=150)
        self.stats_table.column("Game Duration (s)",
                                anchor="center", width=150)
        self.stats_table.pack(fill="both", expand=True)

    def update(self, game_df, waves_df):
        if game_df is None or game_df.empty:
            return

        self.stats_table.delete(*self.stats_table.get_children())

        try:
            waves_stats = game_df['waves_reached'].agg(
                ['min', 'max', 'mean', 'median', 'std']).fillna(0)
            duration_stats = game_df['Time_survived_seconds'].agg(
                ['min', 'max', 'mean', 'median', 'std']).fillna(0)
            waves_mode = game_df['waves_reached'].mode(
            ).iloc[0] if not game_df['waves_reached'].mode().empty else "N/A"
            duration_mode = game_df['Time_survived_seconds'].mode(
            ).iloc[0] if not game_df['Time_survived_seconds'].mode().empty else "N/A"

            stats_to_display = {
                "Min": (waves_stats['min'], duration_stats['min']),
                "Max": (waves_stats['max'], duration_stats['max']),
                "Mean": (f"{waves_stats['mean']:.2f}", f"{duration_stats['mean']:.2f}"),
                "Median": (waves_stats['median'], duration_stats['median']),
                "Mode": (waves_mode, duration_mode),
                "Std Dev": (f"{waves_stats['std']:.2f}", f"{duration_stats['std']:.2f}"),
                "Count": (len(game_df), len(game_df))
            }

            for stat_name, values in stats_to_display.items():
                self.stats_table.insert("", "end", values=(
                    stat_name, values[0], values[1]))
        except Exception as e:
            print(f"Error updating summary stats: {e}")


class TopPlayersVisualization(Visualization):
    def __init__(self, parent):
        super().__init__(parent)

        # Header
        tk.Label(self.frame, text="Top Players by Waves Reached",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self, game_df, waves_df):
        if game_df is None or game_df.empty:
            return

        try:
            self.ax.clear()

            # Group by player and get max waves and min time (for tie-breakers)
            player_stats = game_df.groupby('player_name').agg({
                'waves_reached': 'max',
                'Time_survived_seconds': 'min'
            }).reset_index()

            # Sort by waves (desc) then by time (asc)
            player_stats = player_stats.sort_values(
                by=['waves_reached', 'Time_survived_seconds'],
                ascending=[False, True]
            )

            # Take top 10 players
            top_players = player_stats.head(10)

            # Create bar chart
            bars = self.ax.barh(top_players['player_name'], top_players['waves_reached'],
                                color='skyblue', edgecolor='navy')

            # Add time as annotation for tie-breakers
            for i, (_, row) in enumerate(top_players.iterrows()):
                self.ax.text(row['waves_reached'] + 0.1, i,
                             f"{row['Time_survived_seconds']}s",
                             va='center', fontsize=8)

            self.ax.set_title('Top Players by Waves Reached')
            self.ax.set_xlabel('Waves')
            self.ax.set_ylabel('Player')

            # Add values to bars
            for bar in bars:
                width = bar.get_width()
                self.ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                             f'{width:.0f}', ha='center', va='center')

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating top players chart: {e}")


class SkillsUsageVisualization(Visualization):
    def __init__(self, parent):
        super().__init__(parent)

        # Header
        tk.Label(self.frame, text="Most Popular Skills",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self, game_df, waves_df):
        if game_df is None or game_df.empty:
            return

        try:
            self.ax.clear()

            # Collect all skills
            all_skills = []
            for skill_col in ['skill1', 'skill2', 'skill3', 'skill4']:
                if skill_col in game_df.columns:
                    all_skills.extend(game_df[skill_col].tolist())

            # Count frequencies
            skill_counts = pd.Series(all_skills).value_counts()

            # Get top skills and combine rest as "Others"
            top_skills = skill_counts.head(9)
            others_count = skill_counts[9:].sum() if len(
                skill_counts) > 9 else 0

            if others_count > 0:
                data = top_skills.append(
                    pd.Series([others_count], index=['Others']))
            else:
                data = top_skills

            # Create pie chart
            wedges, texts, autotexts = self.ax.pie(
                data,
                labels=data.index,
                autopct='%1.1f%%',
                textprops={'fontsize': 8},
                colors=plt.cm.tab10.colors
            )

            # Equal aspect ratio ensures pie is drawn as a circle
            self.ax.axis('equal')
            self.ax.set_title('Most Selected Skills')

            # Adjust font size for labels and percentages
            plt.setp(autotexts, size=8, weight='bold')
            plt.setp(texts, size=8)

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating skills pie chart: {e}")


class WaveHistogramVisualization(Visualization):
    def __init__(self, parent):
        super().__init__(parent)

        # Header
        tk.Label(self.frame, text="Wave Distribution",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self, game_df, waves_df):
        if game_df is None or game_df.empty:
            return

        try:
            self.ax.clear()

            # Create histogram of waves reached
            max_wave = game_df['waves_reached'].max()
            bins = range(1, max_wave + 2)  # +2 to include the max value

            n, bins, patches = self.ax.hist(
                game_df['waves_reached'],
                bins=bins,
                edgecolor='black',
                color='skyblue',
                alpha=0.7
            )

            # Add count labels above bars
            for i, count in enumerate(n):
                if count > 0:
                    self.ax.text(
                        bins[i] + 0.5, count + 0.1,
                        int(count),
                        ha='center', va='bottom'
                    )

            self.ax.set_title('Distribution of Waves Reached')
            self.ax.set_xlabel('Wave Number')
            self.ax.set_ylabel('Frequency')
            self.ax.set_xticks(range(1, max_wave + 1))

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating wave histogram: {e}")

# 5. Time vs Waves Scatter Plot


class TimeWavesScatterVisualization(Visualization):
    def __init__(self, parent):
        super().__init__(parent)

        # Header
        tk.Label(self.frame, text="Game Duration vs Waves Reached",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self, game_df, waves_df):
        if game_df is None or game_df.empty:
            return

        try:
            self.ax.clear()

            # Create scatter plot
            scatter = self.ax.scatter(
                game_df['Time_survived_seconds'],
                game_df['waves_reached'],
                c=game_df['player_name'].astype(
                    'category').cat.codes,  # Color by player
                alpha=0.7,
                s=50,
                cmap='tab10'
            )

            # Add player names as annotations
            for i, row in game_df.iterrows():
                self.ax.annotate(
                    row['player_name'],
                    (row['Time_survived_seconds'], row['waves_reached']),
                    fontsize=8,
                    alpha=0.7,
                    xytext=(5, 0),
                    textcoords='offset points'
                )

            # Add best fit line
            if len(game_df) > 1:
                x = game_df['Time_survived_seconds']
                y = game_df['waves_reached']
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                self.ax.plot(x, p(x), "r--", alpha=0.8)

            self.ax.set_title('Game Duration vs Waves Reached')
            self.ax.set_xlabel('Duration (seconds)')
            self.ax.set_ylabel('Waves Reached')

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating time-waves scatter plot: {e}")

# 6. Death Analysis (Correlation Heatmap)


class DeathAnalysisVisualization(Visualization):
    def __init__(self, parent):
        super().__init__(parent)

        # Header
        tk.Label(self.frame, text="Death Analysis Correlation Heatmap",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        # Create matplotlib figure
        self.fig = Figure(figsize=(7, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self, game_df, waves_df):
        if waves_df is None or waves_df.empty:
            return

        try:
            self.ax.clear()

            # Filter for last wave of each game where player died
            last_waves = waves_df.loc[waves_df.groupby('Play_ID')[
                'wave'].idxmax()]

            # Select relevant columns
            corr_cols = ['hp', 'stamina', 'skill1_frequency', 'skill2_frequency',
                         'skill3_frequency', 'skill4_frequency', 'time_per_wave',
                         'spawned_enemies', 'enemies_left']

            # Create correlation matrix
            corr_data = last_waves[corr_cols].corr()

            # Create heatmap
            sns.heatmap(
                corr_data,
                annot=True,
                cmap='coolwarm',
                ax=self.ax,
                fmt='.2f',
                linewidths=0.5,
                annot_kws={"size": 8}
            )

            self.ax.set_title('Correlation Between Factors at Death')

            # Rotate x-axis labels for better visibility
            plt.setp(self.ax.get_xticklabels(), rotation=45,
                     ha='right', rotation_mode='anchor')

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating death analysis: {e}")

# Main Stats Viewer App


class StatsViewerApp:
    def __init__(self, game_csv_path=None, waves_csv_path=None):
        self.game_csv_path = game_csv_path
        self.waves_csv_path = waves_csv_path
        self.game_df = None
        self.waves_df = None
        self.load_data()

    def load_data(self):
        """Load data from CSV files"""
        success = True

        # Load game data
        if not self.game_csv_path or not os.path.exists(self.game_csv_path):
            print(
                f"Warning: Game CSV file not found at {self.game_csv_path}. No game data will be loaded.")
            self.game_df = pd.DataFrame()  # Ensure game_df is an empty DataFrame, not None
            success = False
        else:
            try:
                self.game_df = pd.read_csv(self.game_csv_path)

                # Standardize player name column
                if 'player_name' not in self.game_df.columns and 'name' in self.game_df.columns:
                    print(
                        f"Renaming 'name' column to 'player_name' in game data from {self.game_csv_path}")
                    self.game_df.rename(
                        columns={'name': 'player_name'}, inplace=True)

                # Ensure required columns exist
                required_cols = {
                    'waves_reached': 'numeric',
                    'Time_survived_seconds': 'numeric',
                    'player_name': 'string'  # Ensure this is checked after potential rename
                }

                missing_cols = False
                for col, col_type in required_cols.items():
                    if col not in self.game_df.columns:
                        print(
                            f"Error: Required column '{col}' not found in game data from {self.game_csv_path}.")
                        missing_cols = True
                        success = False  # Mark as not fully successful if essential columns missing
                    elif col_type == 'numeric':  # Only attempt conversion if column exists
                        self.game_df[col] = pd.to_numeric(
                            self.game_df[col], errors='coerce')

                if missing_cols:
                    print(
                        "Essential columns missing from game_df. Some visualizations may fail or be empty.")

                # Ensure skill columns exist, fill with 'unknown' if not present
                for i in range(1, 5):
                    skill_col = f'skill{i}'
                    if skill_col not in self.game_df.columns:
                        self.game_df[skill_col] = 'unknown'

                # Drop rows where essential numeric data couldn't be coerced or is missing
                # but only if the columns actually exist to avoid errors
                cols_to_check_for_na = []
                if 'waves_reached' in self.game_df.columns:
                    cols_to_check_for_na.append('waves_reached')
                if 'Time_survived_seconds' in self.game_df.columns:
                    cols_to_check_for_na.append('Time_survived_seconds')

                if cols_to_check_for_na:
                    self.game_df.dropna(
                        subset=cols_to_check_for_na, inplace=True)

                if self.game_df.empty and success:  # if not already marked as failed due to missing cols
                    print(
                        f"No valid game data after cleaning from {self.game_csv_path}.")
                    # success can remain true if file existed but was empty/all invalid rows

            except Exception as e:
                print(
                    f"Error loading or processing game data from {self.game_csv_path}: {e}")
                self.game_df = pd.DataFrame()  # Ensure game_df is an empty DataFrame on error

        # Load waves data
        if not self.waves_csv_path or not os.path.exists(self.waves_csv_path):
            print(
                f"Warning: Waves CSV file not found at {self.waves_csv_path}. No waves data will be loaded.")
            self.waves_df = pd.DataFrame()  # Ensure waves_df is an empty DataFrame
        else:
            try:
                self.waves_df = pd.read_csv(self.waves_csv_path)

                # Standardize player name column for waves_df
                if 'player_name' not in self.waves_df.columns and 'name' in self.waves_df.columns:
                    print(
                        f"Renaming 'name' column to 'player_name' in waves data from {self.waves_csv_path}")
                    self.waves_df.rename(
                        columns={'name': 'player_name'}, inplace=True)

                # Standardize wave number column for waves_df
                if 'wave' not in self.waves_df.columns and 'waves' in self.waves_df.columns:
                    print(
                        f"Renaming 'waves' column to 'wave' in waves data from {self.waves_csv_path}")
                    self.waves_df.rename(
                        columns={'waves': 'wave'}, inplace=True)

                # Convert numeric columns, add if missing and fill with 0 or NaN then handle
                numeric_cols = ['hp_end_wave', 'stamina_end_wave', 'wave', 'time_per_wave_sec',
                                'spawned_enemies', 'enemies_left']
                # hp -> hp_end_wave, stamina -> stamina_end_wave, time_per_wave -> time_per_wave_sec
                col_renames = {'hp': 'hp_end_wave', 'stamina': 'stamina_end_wave',
                               'time_per_wave': 'time_per_wave_sec'}
                for old_name, new_name in col_renames.items():
                    if old_name in self.waves_df.columns and new_name not in self.waves_df.columns:
                        print(
                            f"Renaming column '{old_name}' to '{new_name}' in waves data.")
                        self.waves_df.rename(
                            columns={old_name: new_name}, inplace=True)

                for col in numeric_cols:
                    if col in self.waves_df.columns:
                        self.waves_df[col] = pd.to_numeric(
                            self.waves_df[col], errors='coerce')
                    else:
                        print(
                            f"Warning: Numeric column '{col}' not found in waves data. It will be ignored or may cause issues.")

                # Convert skill frequency columns
                for i in range(1, 5):
                    freq_col = f'skill{i}_freq'
                    # Check also for skillX_frequency (from earlier iteration)
                    alt_freq_col = f'skill{i}_frequency'
                    if alt_freq_col in self.waves_df.columns and freq_col not in self.waves_df.columns:
                        print(
                            f"Renaming column '{alt_freq_col}' to '{freq_col}' in waves data.")
                        self.waves_df.rename(
                            columns={alt_freq_col: freq_col}, inplace=True)

                    if freq_col in self.waves_df.columns:
                        self.waves_df[freq_col] = pd.to_numeric(
                            self.waves_df[freq_col], errors='coerce').fillna(0)
                    else:
                        # If the column for skill frequency is missing, add it and fill with 0
                        print(
                            f"Warning: Skill frequency column '{freq_col}' not found in waves data. Adding it with default value 0.")
                        self.waves_df[freq_col] = 0

                if self.waves_df.empty:
                    print(
                        f"No valid waves data after cleaning from {self.waves_csv_path}.")
            except Exception as e:
                print(
                    f"Error loading or processing waves data from {self.waves_csv_path}: {e}")
                self.waves_df = pd.DataFrame()  # Ensure waves_df is an empty DataFrame on error

        return success

    def setup_ui(self, root):
        """Set up the UI components"""
        self.root = root
        self.root.title("Incantato Game Statistics")
        self.root.geometry("900x650")

        # Main container frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=5)

        # Tab 1: Summary Statistics
        tab_summary = ttk.Frame(self.notebook)
        self.notebook.add(tab_summary, text="Summary Stats")
        self.summary_vis = SummaryStatsVisualization(tab_summary)

        # Tab 2: Top Players
        tab_players = ttk.Frame(self.notebook)
        self.notebook.add(tab_players, text="Top Players")
        self.players_vis = TopPlayersVisualization(tab_players)

        # Tab 3: Skills Usage
        tab_skills = ttk.Frame(self.notebook)
        self.notebook.add(tab_skills, text="Skills Usage")
        self.skills_vis = SkillsUsageVisualization(tab_skills)

        # Tab 4: Wave Distribution
        tab_wave_hist = ttk.Frame(self.notebook)
        self.notebook.add(tab_wave_hist, text="Wave Distribution")
        self.wave_hist_vis = WaveHistogramVisualization(tab_wave_hist)

        # Tab 5: Time vs Waves
        tab_time_waves = ttk.Frame(self.notebook)
        self.notebook.add(tab_time_waves, text="Time vs Waves")
        self.time_waves_vis = TimeWavesScatterVisualization(tab_time_waves)

        # Tab 6: Death Analysis
        tab_death = ttk.Frame(self.notebook)
        self.notebook.add(tab_death, text="Death Analysis")
        self.death_vis = DeathAnalysisVisualization(tab_death)

        # Store visualizations in a list for easy updates
        self.visualizations = [
            self.summary_vis,
            self.players_vis,
            self.skills_vis,
            self.wave_hist_vis,
            self.time_waves_vis,
            self.death_vis
        ]

        # Add refresh button
        self.refresh_button = ttk.Button(main_frame, text="Refresh Data",
                                         command=self.refresh_data)
        self.refresh_button.pack(pady=(5, 2))

        # Add close button
        self.close_button = ttk.Button(main_frame, text="Close",
                                       command=root.destroy)
        self.close_button.pack(pady=5)

        # Update visualizations with initial data
        self.update_visualizations()

    def refresh_data(self):
        """Reload data and update visualizations"""
        if self.load_data():
            self.update_visualizations()
            print("Data refreshed successfully")
        else:
            print("Failed to refresh data")

    def update_visualizations(self):
        """Update all visualizations with current data"""
        for vis in self.visualizations:
            vis.update(self.game_df, self.waves_df)


# Thread function to run the StatsViewerApp
def _stats_viewer_thread(game_instance, next_state_id_on_close):
    """Thread function to run the StatsViewerApp (for Windows/Linux)"""
    global tk_window_closed

    tk_window_closed = False

    actual_game_csv_path = _get_file_path(C.GAMES_LOG_PATH)
    actual_waves_csv_path = _get_file_path(C.WAVES_LOG_PATH)

    if not actual_game_csv_path:
        print(
            f"Error: Game log file not found at {C.GAMES_LOG_PATH}. Stats will be empty or show no data.")
        # Proceed with None path, App will handle it

    if not actual_waves_csv_path:
        print(
            f"Warning: Waves log file not found at {C.WAVES_LOG_PATH}. Waves-specific stats will be unavailable.")
        # Proceed with None path, App will handle it

    try:
        # Import matplotlib here to avoid conflicts
        import matplotlib
        matplotlib.use('TkAgg')  # Must be before other matplotlib imports
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np

        # Create Tk root window
        root = tk.Tk()

        # Create the app instance
        app = StatsViewerApp(actual_game_csv_path, actual_waves_csv_path)
        app.setup_ui(root)

        # Set up window close event
        def on_close():
            global tk_window_closed
            print("Stats window closing...")
            tk_window_closed = True
            if game_instance and hasattr(game_instance, 'state_manager'):
                print(f"Requesting state change to: {next_state_id_on_close}")
                game_instance.state_manager.set_state(next_state_id_on_close)
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)

        # Start the Tkinter mainloop
        print("Starting Tkinter mainloop in thread...")
        root.mainloop()

    except Exception as e:
        print(f"Exception during Tkinter mainloop: {e}")
    finally:
        print("Tkinter mainloop thread ending.")
        tk_window_closed = True


def run_stats_viewer(game_instance, next_state_id_on_close):
    """
    Launches the stats viewer with platform-specific handling.

    Args:
        game_instance: The game instance that will receive state change requests
        next_state_id_on_close: The state ID to switch to when the viewer is closed

    Returns:
        For macOS: A checker function that the game loop should call periodically
        For other platforms: None
    """
    global tk_stats_thread, tk_window_closed, tk_subprocess, tk_process

    # Store game_instance globally for access during cleanup
    globals()['game_instance'] = game_instance

    if IS_MACOS:
        # On macOS, use a separate process
        print("Running stats viewer in separate process (macOS)")
        process_checker = _run_macos_stats_viewer_process(
            next_state_id_on_close)
        # Return the process checker function for the game to call periodically
        return process_checker
    else:
        # On Windows/Linux, use a thread
        # Check if thread is already running
        if tk_stats_thread and tk_stats_thread.is_alive() and not tk_window_closed:
            print("Stats window thread already running.")
            return None

        print("Launching stats viewer in separate thread...")
        tk_stats_thread = threading.Thread(
            target=_stats_viewer_thread,
            args=(game_instance, next_state_id_on_close),
            daemon=True
        )
        tk_stats_thread.start()
        print(f"Stats viewer thread started")
        return None  # No checker needed for thread approach


# For backwards compatibility
run_stats_viewer_non_blocking = run_stats_viewer


def run_stats_viewer_blocking(game_instance, next_state_id_on_close):
    """
    Legacy function to launch the Tkinter stats window. Blocks execution.
    Closure of the Tkinter window triggers a state change in game_instance.
    On macOS, this will now use the process-based approach to avoid crashes.
    """
    global tk_subprocess, tk_process

    # Store game_instance globally for access during cleanup
    globals()['game_instance'] = game_instance

    if IS_MACOS:
        print("Warning: Using non-blocking process for macOS instead of blocking mode")
        process_checker = run_stats_viewer_non_blocking(
            game_instance, next_state_id_on_close)

        # If we're in a blocking context, wait for the process to finish
        if process_checker:
            print("Waiting for stats viewer process to complete...")
            import time
            try:
                while process_checker():
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error waiting for process: {e}")
            finally:
                # Force state change in case something went wrong
                if hasattr(game_instance, 'state_manager'):
                    game_instance.state_manager.set_state(
                        next_state_id_on_close)
                print("Stats viewer process completed or forced to complete")
    else:
        print("Using blocking stats viewer.")
        _stats_viewer_thread(game_instance, next_state_id_on_close)
        print("Tkinter window closed, mainloop ended.")

    # Always ensure state change before returning
    if hasattr(game_instance, 'state_manager'):
        print(
            f"Ensuring state change to {next_state_id_on_close} before returning")
        game_instance.state_manager.set_state(next_state_id_on_close)


def close_stats_viewer():
    """
    Attempts to close an externally managed Tkinter stats window or process.
    """
    global tk_window_closed, tk_subprocess, tk_process

    print("stats_viewer.close_stats_viewer() called.")

    if IS_MACOS:
        if tk_process and tk_process.is_alive():
            print("Terminating stats viewer process")
            tk_process.terminate()
        elif tk_subprocess and tk_subprocess.poll() is None:
            print("Terminating subprocess")
            tk_subprocess.terminate()
    else:
        tk_window_closed = True


def is_stats_viewer_open():
    """Returns True if the stats viewer is currently open."""
    global tk_stats_thread, tk_window_closed, tk_subprocess, tk_process

    if IS_MACOS:
        return (tk_process and tk_process.is_alive()) or (tk_subprocess and tk_subprocess.poll() is None)
    else:
        return tk_stats_thread and tk_stats_thread.is_alive() and not tk_window_closed


def _run_macos_stats_viewer_process(next_state_id_on_close):
    """
    For macOS only: Launch the stats viewer in a separate process using multiprocessing.
    """
    global tk_process, game_instance

    if tk_process and tk_process.is_alive():
        print("Stats viewer process already running.")
        return None

    actual_game_csv_path = _get_file_path(C.GAMES_LOG_PATH)
    actual_waves_csv_path = _get_file_path(C.WAVES_LOG_PATH)

    if not actual_game_csv_path:
        print(
            f"Error: Game log file not found at {C.GAMES_LOG_PATH}. Cannot start stats viewer process for macOS.")
        # Optionally, trigger state change or handle error more gracefully
        if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
            game_instance.state_manager.set_state(next_state_id_on_close)
        return None  # Critical: game log is essential for the viewer to be useful

    if not actual_waves_csv_path:
        print(
            f"Warning: Waves log file not found at {C.WAVES_LOG_PATH}. Waves-specific stats will be unavailable in macOS process.")
        # Proceed, waves_csv_path can be None

    # Make a temporary copy of the CSV data for the separate process
    # This is important on macOS to avoid issues with file access from a subprocess
    temp_game_csv_path = None
    temp_waves_csv_path = None  # Can remain None if actual_waves_csv_path is None

    try:
        # Game log must exist at this point, so actual_game_csv_path is not None
        temp_game_csv_path = os.path.join(
            tempfile.gettempdir(), f"incantato_game_log_{os.getpid()}.csv")
        shutil.copy2(actual_game_csv_path, temp_game_csv_path)
        # print(f"Copied game log to temporary location for macOS process: {temp_game_csv_path}") # Simplified

        if actual_waves_csv_path:
            temp_waves_csv_path = os.path.join(
                tempfile.gettempdir(), f"incantato_waves_log_{os.getpid()}.csv")
            shutil.copy2(actual_waves_csv_path, temp_waves_csv_path)
            # print(f"Copied waves log to temporary location for macOS process: {temp_waves_csv_path}") # Simplified

    except Exception as e:
        print(
            f"Error copying log files to temporary location for macOS process: {e}.")
        # If copying fails, we probably shouldn't proceed as the subprocess might not have access.
        if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
            game_instance.state_manager.set_state(next_state_id_on_close)
        return None

    exit_flag = multiprocessing.Value('i', 0)
    try:
        # print(f"Launching stats viewer in separate macOS process with game data: {temp_game_csv_path}") # Simplified
        tk_process = multiprocessing.Process(
            target=_run_stats_viewer_app_process,
            args=(temp_game_csv_path, temp_waves_csv_path,
                  exit_flag),  # Pass exit_flag here
            daemon=True
        )
        tk_process.start()
        # print(f"Stats viewer process started (pid: {tk_process.pid})") # Simplified

        # Define a function to check if the process is done
        def check_process():
            if not tk_process.is_alive() or exit_flag.value == 1:
                print("Stats viewer process has ended or signaled completion")
                # Signal to the game to change state
                if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
                    game_instance.state_manager.set_state(
                        next_state_id_on_close)
                return False
            return True

        # Return the checker function
        return check_process

    except Exception as e:
        print(f"Error launching stats viewer process: {e}")
        # Force state change to avoid being stuck
        if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
            game_instance.state_manager.set_state(next_state_id_on_close)
        return None


def _run_stats_viewer_app_process(game_csv_path, waves_csv_path, exit_flag):
    """Run the stats viewer app in a separate process for macOS"""
    try:
        # ALL IMPORTS NEEDED BY StatsViewerApp AND ITS VISUALIZATION SUBCLASSES
        # MUST BE HERE.
        import tkinter as tk
        from tkinter import ttk
        import pandas as pd

        import matplotlib
        matplotlib.use('TkAgg')
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        import os
        import tempfile
        import sys  # Potentially for other system-level things if used by pandas/matplotlib indirectly

        # print(f"Starting stats viewer app process with data at: {game_csv_path}") # Essential debug print, keep

        root = tk.Tk()
        # NOTE: The StatsViewerApp class definition and all Visualization subclasses
        # must be self-contained or their definitions passed/available to this process.
        # Python's multiprocessing on macOS (with 'spawn' start method by default)
        # means this function runs in a new process that doesn't inherit globals in the same way a thread would.
        # If StatsViewerApp is defined in the same file, it should be okay.
        app = StatsViewerApp(game_csv_path, waves_csv_path)
        app.setup_ui(root)

        def on_close():
            print("Stats viewer window closing...")
            exit_flag.value = 1
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()
        exit_flag.value = 1  # Ensure flag is set if mainloop exits cleanly
        # print("Stats viewer process: Tkinter mainloop ended") # Debug feedback, keep

    except Exception as e:
        print(f"Exception in stats viewer app process: {e}")
        if 'exit_flag' in locals() and exit_flag:
            exit_flag.value = 1
        import traceback
        traceback.print_exc()  # This will give more details on the error
