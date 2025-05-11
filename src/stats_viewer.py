"""
Stats Viewer module for Incantato game.

This module provides visualization tools for analyzing game statistics through a graphical interface.
It displays various metrics such as player performance, skills usage, and wave progression
using Matplotlib charts embedded in a Tkinter GUI.
"""

from matplotlib.figure import Figure
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.lines as mlines
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
from config import Config as C

# Ensure Matplotlib TkAgg backend is explicitly imported for main thread/non-macOS use
import matplotlib
matplotlib.use('TkAgg')

# Global variables for tracking
tk_stats_thread = None
tk_window_closed = False
tk_subprocess = None
tk_process = None
IS_MACOS = platform.system() == 'Darwin'


def _get_file_path(configured_path):
    """
    Resolves the actual file path from a configured path.

    Attempts to find a file using several strategies:
    1. Try the absolute path directly
    2. Try relative to the project root
    3. Try relative to the current working directory

    Args:
        configured_path: The path as configured in the settings

    Returns:
        str: Absolute path to the file if found, None otherwise
    """
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
    """
    Base class for all visualization components.

    Provides a common interface for visualizations to be embedded in the main app.
    Each subclass should implement its own rendering of game statistics.
    """

    def __init__(self, parent):
        """
        Initialize a visualization component.

        Args:
            parent: The parent Tkinter widget where this visualization will be placed
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)

    def update(self, game_df, waves_df):
        """
        Update the visualization with new data.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data
        """
        pass


class SummaryStatsVisualization(Visualization):
    """
    Displays summary statistics for game performance in a tabular format.

    Shows min, max, mean, median, mode, and standard deviation for key metrics
    such as waves reached and game duration.
    """

    def __init__(self, parent):
        """
        Initialize the summary stats visualization.

        Args:
            parent: The parent Tkinter widget
        """
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
        """
        Update the summary statistics with new game data.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data (not used in this visualization)
        """
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
    """
    Displays a bar chart of top players ranked by waves reached.

    Shows players sorted by their highest wave achievement, with time as a tiebreaker.
    Includes time information as annotations on the bars.
    """

    def __init__(self, parent):
        """
        Initialize the top players visualization.

        Args:
            parent: The parent Tkinter widget
        """
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
        """
        Update the top players visualization with new game data.

        Creates a horizontal bar chart showing the top players by waves reached,
        with survival time as a tiebreaker.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data (not used in this visualization)
        """
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

            self.ax.invert_yaxis()  # Ensure the top player is at the top of the chart

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating top players chart: {e}")


class SkillsUsageVisualization(Visualization):
    """
    Displays a pie chart of the most frequently used skills.

    Shows the distribution of skill selections across all games,
    highlighting the most popular choices.
    """

    def __init__(self, parent):
        """
        Initialize the skills usage visualization.

        Args:
            parent: The parent Tkinter widget
        """
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
        """
        Update the skills usage visualization with new game data.

        Creates a pie chart showing the distribution of skills used across all games.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data (not used in this visualization)
        """
        if game_df is None or game_df.empty:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No game data available for skill analysis.",
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, fontsize=10)
            self.fig.tight_layout()
            self.canvas.draw_idle()
            return

        try:
            self.ax.clear()
            all_skills_raw = []
            for skill_col in ['skill1', 'skill2', 'skill3', 'skill4']:
                if skill_col in game_df.columns:
                    all_skills_raw.extend(
                        game_df[skill_col].astype(str).tolist())
            filtered_skills = [
                s.strip() for s in all_skills_raw
                if s.strip().lower() not in {'', 'unknown', 'nan', 'none', '<na>'}
            ]
            if not filtered_skills:
                self.ax.text(0.5, 0.5, "No valid skill usage data to display.",
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes, fontsize=10)
                self.fig.tight_layout()
                self.canvas.draw_idle()
                return
            skill_counts = pd.Series(filtered_skills).value_counts()

            # Get top 7 skills and combine rest as "Others"
            top_skills = skill_counts.head(7)
            others_count = skill_counts[7:].sum() if len(
                skill_counts) > 7 else 0

            if others_count > 0:
                data = pd.concat([top_skills, pd.Series(
                    [others_count], index=['Others'])])
            else:
                data = top_skills

            wedges, texts, autotexts = self.ax.pie(
                data,
                labels=data.index,
                # Hide small percentages
                autopct=lambda p: f'{p:.1f}%' if p >= 1 else '',
                textprops={'fontsize': 8},
                colors=plt.cm.tab10.colors,
                startangle=140
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
    """
    Displays a histogram of waves reached across all games.

    Shows the distribution of game outcomes based on how far players progressed.
    """

    def __init__(self, parent):
        """
        Initialize the wave distribution visualization.

        Args:
            parent: The parent Tkinter widget
        """
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
        """
        Update the wave histogram visualization with new game data.

        Creates a histogram showing the distribution of how far players reached in games.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data (not used in this visualization)
        """
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

            for i, count in enumerate(n):
                if count > 0:
                    bar_center = (bins[i] + bins[i+1]) / 2
                    self.ax.text(
                        bar_center, count / 2,
                        int(count),
                        ha='center', va='center', fontsize=10, color='black'
                    )

            self.ax.set_title('Distribution of Waves Reached')
            self.ax.set_xlabel('Wave Number')
            self.ax.set_ylabel('Frequency')
            self.ax.set_xticks(range(1, max_wave + 1))

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating wave histogram: {e}")


class TopDecksVisualization(Visualization):
    """
    Displays a bar chart of the most frequently used skill combinations (decks).

    Identifies common skill groupings and displays their frequency of use,
    helping identify popular strategies.
    """

    def __init__(self, parent):
        """
        Initialize the top decks visualization.

        Args:
            parent: The parent Tkinter widget
        """
        super().__init__(parent)
        tk.Label(self.frame, text="Top 7 Most Frequent Decks",
                 font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        # Adjusted size for potentially long deck names
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update(self, game_df, waves_df):
        """
        Update the top decks visualization with new game data.

        Creates a horizontal bar chart showing the most frequently used skill combinations.
        Skills are sorted within each deck for consistent grouping.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data (not used in this visualization)
        """
        if game_df is None or game_df.empty:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No game data available for deck analysis.",
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes)
            self.canvas.draw_idle()
            return

        try:
            self.ax.clear()

            # Create a 'deck' column by combining skill columns
            # Sort skills within each deck for consistent grouping
            def create_deck_tuple(row):
                skills = sorted([str(row[f'skill{i}']) for i in range(1, 5) if pd.notna(
                    row[f'skill{i}']) and row[f'skill{i}'] != 'unknown'])
                return tuple(skills)

            game_df['deck'] = game_df.apply(create_deck_tuple, axis=1)

            # Count deck frequencies
            all_deck_counts = game_df['deck'].value_counts()

            if all_deck_counts.empty:
                self.ax.text(0.5, 0.5, "Not enough data to determine top decks.",
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes)
                self.canvas.draw_idle()
                return

            # Get top 7 decks and combine rest as "Others"
            top_n = 7
            top_decks_series = all_deck_counts.head(top_n)
            others_count = all_deck_counts[top_n:].sum()

            data_to_plot = top_decks_series
            if others_count > 0:
                others_label_tuple = ("Others",)
                data_to_plot = pd.concat([data_to_plot, pd.Series(
                    [others_count], index=[others_label_tuple])])

            if data_to_plot.empty:  # Should not happen if all_deck_counts was not empty
                self.ax.text(0.5, 0.5, "No deck data to display after processing.",
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes)
                self.canvas.draw_idle()
                return

            # Convert deck tuples to strings for display
            # Join with newline for better wrapping
            deck_labels = ['\n'.join(deck) if isinstance(
                deck, tuple) else str(deck) for deck in data_to_plot.index]

            bars = self.ax.barh(deck_labels, data_to_plot.values,
                                color='mediumpurple', edgecolor='indigo')
            self.ax.set_title('Top 7 Most Frequent Decks')
            self.ax.set_xlabel('Frequency')
            self.ax.set_ylabel('Deck Composition')
            self.ax.invert_yaxis()  # Display the most frequent at the top

            # Add frequency numbers to bars
            for bar in bars:
                self.ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                             f'{int(bar.get_width())}', va='center', ha='left', fontsize=9)

            self.fig.tight_layout(pad=1.5)  # Adjust padding
            self.canvas.draw_idle()

        except Exception as e:
            print(f"Error updating top decks chart: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Error: {e}",
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, color='red')
            self.canvas.draw_idle()


class TimeWavesScatterVisualization(Visualization):
    """
    Displays a scatter plot of game duration versus waves reached.

    Shows the relationship between time spent and game progress, with 
    interactive tooltips and a best-fit line to identify trends.
    Each point represents a game, colored by player.
    """

    def __init__(self, parent):
        """
        Initialize the time vs waves scatter plot visualization.

        Creates an interactive scatter plot with hover tooltips.

        Args:
            parent: The parent Tkinter widget
        """
        super().__init__(parent)
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.scatter_points = None
        self.annot = None  # For hover annotations

        # Set up hover annotations
        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(20, 20),
                                      textcoords="offset points",
                                      bbox=dict(boxstyle="round",
                                                fc="w", alpha=0.7),
                                      arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        # Connect hover events
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def hover(self, event):
        """
        Handle hover events on scatter plot points.

        Displays tooltips when hovering over data points.

        Args:
            event: Matplotlib event object containing cursor position
        """
        if not hasattr(self, 'scatter_points') or self.scatter_points is None:
            return

        if event.inaxes == self.ax:
            cont, ind = self.scatter_points.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if self.annot.get_visible():
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def update_annot(self, ind):
        """
        Update the annotation content when hovering over a point.

        Args:
            ind: Index of the data point under the cursor
        """
        if not hasattr(self, 'game_data') or self.game_data is None:
            return

        pos = self.scatter_points.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos

        idx = ind["ind"][0]
        player = self.game_data.iloc[idx]['player_name']
        waves = self.game_data.iloc[idx]['waves_reached']
        time = self.game_data.iloc[idx]['Time_survived_seconds']

        text = f"{player}\nWaves: {waves}\nTime: {time:.1f}s"
        self.annot.set_text(text)

    def update(self, game_df, waves_df):
        """
        Update the scatter plot with new game data.

        Creates a scatter plot showing the relationship between game duration and waves reached,
        with a best-fit line to visualize the trend. Points are colored by player name.

        Args:
            game_df: DataFrame containing game data
            waves_df: DataFrame containing wave-specific data (not used in this visualization)
        """
        try:
            if game_df is None or game_df.empty:
                self.ax.clear()
                self.ax.set_title('No game data available')
                self.fig.tight_layout()
                self.canvas.draw_idle()
                return

            # Keep a reference to the data for hover tooltips
            self.game_data = game_df.copy()

            # Clear previous plot
            self.ax.clear()

            # Create scatter plot with improved visual style
            self.scatter_points = self.ax.scatter(
                game_df['Time_survived_seconds'],
                game_df['waves_reached'],
                c=game_df['player_name'].astype('category').cat.codes,
                alpha=0.7,
                s=80,  # Larger points
                cmap='tab10',
                edgecolors='white',  # White edges make points stand out
                linewidths=0.5
            )

            # Add best fit line with confidence interval
            if len(game_df) > 1:
                try:
                    x = game_df['Time_survived_seconds']
                    y = game_df['waves_reached']

                    # Add polynomial fit
                    z = np.polyfit(x, y, 1)
                    p = np.poly1d(z)
                    x_range = np.linspace(min(x), max(x), 100)
                    self.ax.plot(x_range, p(x_range), "r--", alpha=0.8,
                                 label=f"Best fit: y={z[0]:.3f}x+{z[1]:.2f}")

                    # Add confidence interval if seaborn is available and there are enough points
                    if len(x) >= 3:
                        sns.regplot(x=x, y=y, scatter=False, ax=self.ax,
                                    color='r', line_kws={'alpha': 0.0},
                                    ci=95)
                except Exception as e:
                    print(f"Error creating best fit line: {e}")

            # Improve chart styling
            self.ax.set_title(
                'Player Performance: Game Duration vs Waves Reached', fontsize=12)
            self.ax.set_xlabel('Duration (seconds)', fontsize=10)
            self.ax.set_ylabel('Waves Reached', fontsize=10)
            self.ax.grid(True, linestyle='--', alpha=0.7)

            # Add zero lines
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)

            # Create a better legend with colored dots
            unique_players = game_df['player_name'].unique()
            player_categories = game_df['player_name'].astype('category').cat
            player_codes = {player: code for player, code in zip(
                player_categories.categories, range(len(player_categories.categories)))}

            legend_handles = []
            cmap = plt.get_cmap('tab10')  # Ensure we use the same colormap

            for player_name in unique_players:
                if player_name in player_codes:
                    # Cycle through 10 colors
                    player_color = cmap(player_codes[player_name] % 10 / 10.0)
                    legend_handles.append(mlines.Line2D(
                        [], [],
                        color=player_color,
                        marker='o',
                        linestyle='None',
                        markeredgecolor='white',
                        markeredgewidth=0.5,
                        markersize=8,
                        label=player_name
                    ))

            # Add legend for best fit line if it exists
            if len(game_df) > 1:
                legend_handles.append(mlines.Line2D(
                    [], [],
                    color='r',
                    linestyle='--',
                    markersize=0,
                    label=f"Best fit"
                ))

            if legend_handles:
                self.ax.legend(
                    handles=legend_handles,
                    title="Players",
                    fontsize='small',
                    title_fontsize='medium',
                    loc='best',
                    framealpha=0.8,
                    edgecolor='lightgray'
                )

            self.fig.tight_layout()
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating time-waves scatter plot: {e}")
            self.ax.clear()
            self.ax.set_title(f'Error updating plot')
            self.fig.tight_layout()
            self.canvas.draw_idle()


class StatsViewerApp:
    """
    Main application for visualizing game statistics.

    Loads data from CSV files and creates a tabbed interface with different
    visualizations of game performance metrics.
    """

    def __init__(self, game_csv_path=None, waves_csv_path=None):
        """
        Initialize the StatsViewerApp with data sources.

        Args:
            game_csv_path: Path to the CSV file containing game data
            waves_csv_path: Path to the CSV file containing wave-specific data
        """
        self.game_csv_path = game_csv_path
        self.waves_csv_path = waves_csv_path
        self.game_df = None
        self.waves_df = None
        self.load_data()

    def load_data(self):
        """
        Load and preprocess data from CSV files.

        Handles column standardization, data type conversion, and validation.

        Returns:
            bool: True if data was loaded successfully, False otherwise
        """
        success = True

        # Load game data
        if not self.game_csv_path or not os.path.exists(self.game_csv_path):
            print(
                f"Warning: Game CSV file not found at {self.game_csv_path}. No game data will be loaded.")
            self.game_df = pd.DataFrame()
            success = False
        else:
            try:
                self.game_df = pd.read_csv(self.game_csv_path)

                # Standardize player name column
                if 'player_name' not in self.game_df.columns and 'name' in self.game_df.columns:
                    self.game_df.rename(
                        columns={'name': 'player_name'}, inplace=True)

                # Ensure required columns exist
                required_cols = {
                    'waves_reached': 'numeric',
                    'Time_survived_seconds': 'numeric',
                    'player_name': 'string'
                }

                missing_cols = False
                for col, col_type in required_cols.items():
                    if col not in self.game_df.columns:
                        print(
                            f"Error: Required column '{col}' not found in game data.")
                        missing_cols = True
                        success = False
                    elif col_type == 'numeric':
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
                cols_to_check_for_na = []
                if 'waves_reached' in self.game_df.columns:
                    cols_to_check_for_na.append('waves_reached')
                if 'Time_survived_seconds' in self.game_df.columns:
                    cols_to_check_for_na.append('Time_survived_seconds')

                if cols_to_check_for_na:
                    self.game_df.dropna(
                        subset=cols_to_check_for_na, inplace=True)

                if self.game_df.empty and success:
                    print(f"No valid game data after cleaning.")

            except Exception as e:
                print(f"Error loading or processing game data: {e}")
                self.game_df = pd.DataFrame()
                success = False

        # Load waves data
        if not self.waves_csv_path or not os.path.exists(self.waves_csv_path):
            print(
                f"Warning: Waves CSV file not found at {self.waves_csv_path}. No waves data will be loaded.")
            self.waves_df = pd.DataFrame()
        else:
            try:
                self.waves_df = pd.read_csv(self.waves_csv_path)

                # Standardize player name column for waves_df
                if 'player_name' not in self.waves_df.columns and 'name' in self.waves_df.columns:
                    print(f"Renaming 'name' column to 'player_name' in waves data")
                    self.waves_df.rename(
                        columns={'name': 'player_name'}, inplace=True)

                # Standardize wave number column for waves_df
                if 'wave' not in self.waves_df.columns and 'waves' in self.waves_df.columns:
                    print(f"Renaming 'waves' column to 'wave' in waves data")
                    self.waves_df.rename(
                        columns={'waves': 'wave'}, inplace=True)

                # Convert numeric columns, add if missing and fill with 0 or NaN then handle
                numeric_cols = ['hp_end_wave', 'stamina_end_wave', 'wave', 'time_per_wave_sec',
                                'spawned_enemies', 'enemies_left']

                # Column rename mappings
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
                            f"Warning: Numeric column '{col}' not found in waves data.")

                # Convert skill frequency columns
                for i in range(1, 5):
                    freq_col = f'skill{i}_freq'
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
                    print(f"No valid waves data after cleaning.")
            except Exception as e:
                print(f"Error loading or processing waves data: {e}")
                self.waves_df = pd.DataFrame()

        return success

    def setup_ui(self, root):
        """
        Set up the user interface components.

        Creates tabs for different visualizations and sets up the main window structure.

        Args:
            root: The Tkinter root window
        """
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

        # Tab for Top Decks
        tab_top_decks = ttk.Frame(self.notebook)
        self.notebook.add(tab_top_decks, text="Top Decks")
        self.top_decks_vis = TopDecksVisualization(tab_top_decks)

        # Tab 5: Time vs Waves
        tab_time_waves = ttk.Frame(self.notebook)
        self.notebook.add(tab_time_waves, text="Time vs Waves")
        self.time_waves_vis = TimeWavesScatterVisualization(tab_time_waves)

        # Store visualizations in a list for easy updates
        self.visualizations = [
            self.summary_vis,
            self.players_vis,
            self.skills_vis,
            self.wave_hist_vis,
            self.top_decks_vis,
            self.time_waves_vis,
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
        """
        Reload data from source files and update all visualizations.
        """
        if self.load_data():
            self.update_visualizations()
            print("Data refreshed successfully")
        else:
            print("Failed to refresh data")

    def update_visualizations(self):
        """
        Update all visualization components with current data.
        """
        for vis in self.visualizations:
            vis.update(self.game_df, self.waves_df)


def _stats_viewer_thread(game_instance, next_state_id_on_close):
    """
    Thread function to run the StatsViewerApp (for Windows/Linux).

    Creates a Tkinter window in a separate thread and handles state changes
    when the window is closed.

    Args:
        game_instance: The game instance that will receive state change requests
        next_state_id_on_close: The state ID to switch to when the viewer is closed
    """
    global tk_window_closed
    tk_window_closed = False

    actual_game_csv_path = _get_file_path(C.GAMES_LOG_PATH)
    actual_waves_csv_path = _get_file_path(C.WAVES_LOG_PATH)

    if not actual_game_csv_path:
        print(
            f"Error: Game log file not found at {C.GAMES_LOG_PATH}. Stats will be empty or show no data.")

    if not actual_waves_csv_path:
        print(
            f"Warning: Waves log file not found at {C.WAVES_LOG_PATH}. Waves-specific stats will be unavailable.")

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
    Legacy function to launch the Tkinter stats window in blocking mode.

    Closure of the Tkinter window triggers a state change in game_instance.
    On macOS, this will use the process-based approach to avoid crashes.

    Args:
        game_instance: The game instance that will receive state change requests
        next_state_id_on_close: The state ID to switch to when the viewer is closed
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

    Handles both thread-based and process-based viewer implementations.
    """
    global tk_window_closed, tk_subprocess, tk_process

    print("Closing stats viewer window if open.")

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
    """
    Checks if the stats viewer is currently open.

    Returns:
        bool: True if the stats viewer is currently open, False otherwise
    """
    global tk_stats_thread, tk_window_closed, tk_subprocess, tk_process

    if IS_MACOS:
        return (tk_process and tk_process.is_alive()) or (tk_subprocess and tk_subprocess.poll() is None)
    else:
        return tk_stats_thread and tk_stats_thread.is_alive() and not tk_window_closed


def _run_macos_stats_viewer_process(next_state_id_on_close):
    """
    For macOS only: Launch the stats viewer in a separate process using multiprocessing.

    Creates a multiprocessing.Process to run the stats viewer to avoid
    issues with Tkinter on macOS.

    Args:
        next_state_id_on_close: The state ID to switch to when the viewer is closed

    Returns:
        function: A checker function that should be called periodically to detect process completion
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
        # Trigger state change since we can't proceed
        if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
            game_instance.state_manager.set_state(next_state_id_on_close)
        return None

    if not actual_waves_csv_path:
        print(
            f"Warning: Waves log file not found at {C.WAVES_LOG_PATH}. Waves-specific stats will be unavailable in macOS process.")

    # Make a temporary copy of the CSV data for the separate process
    # This is important on macOS to avoid issues with file access from a subprocess
    temp_game_csv_path = None
    temp_waves_csv_path = None

    try:
        # Game log must exist at this point, so actual_game_csv_path is not None
        temp_game_csv_path = os.path.join(
            tempfile.gettempdir(), f"incantato_game_log_{os.getpid()}.csv")
        shutil.copy2(actual_game_csv_path, temp_game_csv_path)

        if actual_waves_csv_path:
            temp_waves_csv_path = os.path.join(
                tempfile.gettempdir(), f"incantato_waves_log_{os.getpid()}.csv")
            shutil.copy2(actual_waves_csv_path, temp_waves_csv_path)

    except Exception as e:
        print(
            f"Error copying log files to temporary location for macOS process: {e}.")
        # If copying fails, we probably shouldn't proceed as the subprocess might not have access.
        if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
            game_instance.state_manager.set_state(next_state_id_on_close)
        return None

    exit_flag = multiprocessing.Value('i', 0)
    try:
        print("Launching stats viewer in separate macOS process")
        tk_process = multiprocessing.Process(
            target=_run_stats_viewer_app_process,
            args=(temp_game_csv_path, temp_waves_csv_path, exit_flag),
            daemon=True
        )
        tk_process.start()
        print(f"Stats viewer process started (pid: {tk_process.pid})")

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
    """
    Run the stats viewer app in a separate process for macOS.

    Args:
        game_csv_path: Path to the CSV file containing game data
        waves_csv_path: Path to the CSV file containing wave-specific data
        exit_flag: Shared multiprocessing value to signal completion
    """
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
        import sys

        print(f"Starting stats viewer app process")

        root = tk.Tk()
        app = StatsViewerApp(game_csv_path, waves_csv_path)
        app.setup_ui(root)

        def on_close():
            print("Stats viewer window closing...")
            exit_flag.value = 1
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()
        exit_flag.value = 1  # Ensure flag is set if mainloop exits cleanly
        print("Stats viewer process: Tkinter mainloop ended")

    except Exception as e:
        print(f"Exception in stats viewer app process: {e}")
        if 'exit_flag' in locals() and exit_flag:
            exit_flag.value = 1
        import traceback
        traceback.print_exc()  # This will give more details on the error
