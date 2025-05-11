import os
import pandas as pd
import threading
import tkinter as tk
from tkinter import ttk
import platform
import subprocess
import sys
import tempfile
import shutil

# Don't import matplotlib here in the main module
# It will be imported in the subprocess on macOS

try:
    from config import Config as C
    # Prefer LOG_GAME_SESSION_CSV, then LOG_CSV, then a default.
    LOG_CSV_FILENAME = 'log_game_session.csv'  # The target file
    LOG_GAME_CSV_PATH = getattr(C, 'LOG_GAME_SESSION_CSV', None)
    if LOG_GAME_CSV_PATH is None:
        # Fallback to generic LOG_CSV
        LOG_GAME_CSV_PATH = getattr(C, 'LOG_CSV', None)

    if LOG_GAME_CSV_PATH is None:  # If still None, construct from base path
        log_base_path = getattr(C, 'LOG_BASE_PATH', 'data')
        LOG_GAME_CSV_PATH = os.path.join(log_base_path, LOG_CSV_FILENAME)

except ImportError:
    print("Warning: config.py not found. Using default path 'data/log_game_session.csv'")
    LOG_GAME_CSV_PATH = 'data/log_game_session.csv'


# Global variables for tracking
tk_stats_thread = None
tk_window_closed = False
tk_subprocess = None
IS_MACOS = platform.system() == 'Darwin'


def _get_actual_log_path():
    """Tries to find the log file, returning its absolute path if found."""
    # Try the configured path directly (it might be absolute or correctly relative)
    if os.path.exists(LOG_GAME_CSV_PATH):
        return os.path.abspath(LOG_GAME_CSV_PATH)

    # Try relative to the script's directory's parent (common for src/data structure)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    path_relative_to_parent = os.path.abspath(
        os.path.join(current_script_dir, '..', LOG_GAME_CSV_PATH))
    if os.path.exists(path_relative_to_parent):
        return path_relative_to_parent

    # Try relative to current working directory (if CWD is workspace root)
    path_relative_to_cwd = os.path.abspath(LOG_GAME_CSV_PATH)
    # This might be the same as the first check
    if os.path.exists(path_relative_to_cwd):
        return path_relative_to_cwd

    # Last attempt: look for data directory in standard locations
    possible_data_dirs = [
        os.path.join(current_script_dir, '..', 'data'),
        os.path.join(os.getcwd(), 'data'),
    ]

    for data_dir in possible_data_dirs:
        if os.path.isdir(data_dir):
            possible_file = os.path.join(
                data_dir, os.path.basename(LOG_GAME_CSV_PATH))
            if os.path.exists(possible_file):
                return os.path.abspath(possible_file)

    # Create a dummy file if nothing found
    return _create_dummy_log_file()


def _create_dummy_log_file():
    """Creates a dummy log file for testing if none exists."""
    print("Creating a dummy log file for testing.")
    try:
        # Create a temporary file
        dummy_dir = os.path.join(tempfile.gettempdir(), "incantato_stats")
        os.makedirs(dummy_dir, exist_ok=True)
        dummy_path = os.path.join(dummy_dir, "dummy_log_game_session.csv")

        # Create test data
        dummy_data = {
            'player_name': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5'],
            'waves_reached': [3, 5, 2, 7, 4],
            'Time_survived_seconds': [45, 120, 30, 180, 60]
        }

        # Write to CSV
        pd.DataFrame(dummy_data).to_csv(dummy_path, index=False)
        print(f"Created dummy log at: {dummy_path}")
        return dummy_path
    except Exception as e:
        print(f"Error creating dummy file: {e}")
        return None


# This function runs in a normal thread and is safe for Windows/Linux
def _load_and_display_stats(data_frame, fig_canvas=None):
    """Loads data from the log file and displays summary statistics and charts."""
    # Only import matplotlib if needed (when fig_canvas is provided)
    if fig_canvas:
        try:
            import matplotlib
            matplotlib.use('TkAgg')
            from matplotlib.figure import Figure
        except ImportError:
            print("Warning: Matplotlib not available; charts will not be shown")
            fig_canvas = None

    data_frame.delete(*data_frame.get_children())

    actual_log_path = _get_actual_log_path()

    if not actual_log_path:
        error_message = f"Error: Log file '{os.path.basename(LOG_GAME_CSV_PATH)}' not found.\\nChecked default logic with base path: {LOG_GAME_CSV_PATH}"
        tk.Label(data_frame.master, text=error_message).pack(pady=10)
        print(error_message)  # Also print to console for debugging
        return None

    try:
        df = pd.read_csv(actual_log_path)
        if df.empty:
            tk.Label(data_frame.master, text="Log file is empty.").pack(pady=10)
            return None

        required_cols = {'waves_reached': 'numeric',
                         'Time_survived_seconds': 'numeric'}
        for col, col_type in required_cols.items():
            if col not in df.columns:
                tk.Label(
                    data_frame.master, text=f"Error: Column '{col}' not found in {os.path.basename(actual_log_path)}.").pack(pady=5)
                return None
            if col_type == 'numeric':
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df.dropna(subset=[col], inplace=True)

        if df.empty:
            tk.Label(data_frame.master, text="No valid numeric data after cleaning.").pack(
                pady=10)
            return None

        waves_stats = df['waves_reached'].agg(
            ['min', 'max', 'mean', 'median', 'std']).fillna(0)
        duration_stats = df['Time_survived_seconds'].agg(
            ['min', 'max', 'mean', 'median', 'std']).fillna(0)
        waves_mode = df['waves_reached'].mode()
        duration_mode = df['Time_survived_seconds'].mode()

        stats_to_display = {
            "Min": (waves_stats.get('min', 0), duration_stats.get('min', 0)),
            "Max": (waves_stats.get('max', 0), duration_stats.get('max', 0)),
            "Mean": (f"{waves_stats.get('mean', 0):.2f}", f"{duration_stats.get('mean', 0):.2f}"),
            "Median": (waves_stats.get('median', 0), duration_stats.get('median', 0)),
            "Mode": (", ".join(map(str, waves_mode)) if not waves_mode.empty else "N/A",
                     ", ".join(map(str, duration_mode)) if not duration_mode.empty else "N/A"),
            "Std Dev": (f"{waves_stats.get('std', 0):.2f}", f"{duration_stats.get('std', 0):.2f}"),
        }
        for stat_name, values in stats_to_display.items():
            data_frame.insert("", "end", values=(
                stat_name, values[0], values[1]))

        # Update the matplotlib figure if provided
        if fig_canvas and hasattr(fig_canvas, 'figure'):
            fig = fig_canvas.figure
            fig.clear()

            # Create two subplots for waves and duration
            ax1 = fig.add_subplot(211)  # Top plot
            ax2 = fig.add_subplot(212)  # Bottom plot

            # Waves reached histogram
            ax1.hist(df['waves_reached'], bins=10,
                     color='skyblue', edgecolor='black')
            ax1.set_title('Waves Reached Distribution')
            ax1.set_xlabel('Waves')
            ax1.set_ylabel('Frequency')

            # Time survived histogram
            ax2.hist(df['Time_survived_seconds'], bins=10,
                     color='lightgreen', edgecolor='black')
            ax2.set_title('Game Duration Distribution')
            ax2.set_xlabel('Seconds')
            ax2.set_ylabel('Frequency')

            fig.tight_layout()
            fig_canvas.draw_idle()  # More efficient than draw()

        return df

    except pd.errors.EmptyDataError:
        tk.Label(data_frame.master,
                 text=f"Log file '{os.path.basename(actual_log_path)}' is empty or not a valid CSV.").pack(pady=10)
    except Exception as e:
        error_text = f"An error occurred while loading stats:\\n{e}\\nLog path tried: {actual_log_path}"
        tk.Label(data_frame.master, text=error_text).pack(pady=10)
        print(
            f"Error in _load_and_display_stats: {e}, Path: {actual_log_path}")

    return None


def _stats_viewer_thread(game_instance, next_state_id_on_close):
    """Thread function that creates and runs the Tkinter window for non-macOS platforms."""
    global tk_window_closed

    tk_window_closed = False
    root = tk.Tk()
    root.title("Game Statistics")
    root.geometry("800x600")

    # Main container frame
    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.pack(fill="both", expand=True)

    # Create notebook (tabbed interface)
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True, pady=5)

    # Tab 1: Statistics Table
    tab_stats = ttk.Frame(notebook)
    notebook.add(tab_stats, text="Statistics")

    # Add refresh button to stats tab
    refresh_button = ttk.Button(tab_stats, text="Refresh Data")
    refresh_button.pack(pady=(5, 10))

    # Stats table
    stats_table = ttk.Treeview(tab_stats, columns=(
        "Statistic", "Waves Reached", "Game Duration (s)"), show="headings")
    stats_table.heading("Statistic", text="Statistic")
    stats_table.heading("Waves Reached", text="Waves Reached")
    stats_table.heading("Game Duration (s)", text="Game Duration (s)")
    stats_table.column("Statistic", anchor="w", width=100)
    stats_table.column("Waves Reached", anchor="center", width=150)
    stats_table.column("Game Duration (s)", anchor="center", width=150)
    stats_table.pack(fill="both", expand=True, padx=5, pady=5)

    try:
        # Import matplotlib here (non-macOS only) to avoid conflicts
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        # Tab 2: Charts
        tab_charts = ttk.Frame(notebook)
        notebook.add(tab_charts, text="Charts")

        # Create matplotlib figure and canvas
        fig = Figure(figsize=(8, 6), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=tab_charts)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure refresh button to update both tabs
        refresh_button.config(
            command=lambda: _load_and_display_stats(stats_table, canvas))

    except ImportError:
        # If matplotlib not available, just use the stats table
        print("Warning: Matplotlib not available; only showing statistics table")
        refresh_button.config(
            command=lambda: _load_and_display_stats(stats_table))
        canvas = None

    # Initial data load
    df = _load_and_display_stats(
        stats_table, canvas if 'canvas' in locals() else None)

    def on_close():
        global tk_window_closed
        print("Stats window closing...")
        tk_window_closed = True
        if game_instance and hasattr(game_instance, 'state_manager'):
            print(
                f"Requesting Pygame state change to: {next_state_id_on_close}")
            game_instance.state_manager.set_state(next_state_id_on_close)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.resizable(True, True)

    try:
        print("Starting Tkinter mainloop in thread...")
        root.mainloop()
    except Exception as e:
        print(f"Exception during Tkinter mainloop: {e}")
    finally:
        print("Tkinter mainloop thread ending.")
        tk_window_closed = True


def _run_macos_stats_viewer_process(next_state_id_on_close):
    """
    For macOS only: Launch the stats viewer in a separate process.
    Creates a simple Python script that launches Tkinter in the main thread.
    """
    global tk_subprocess, game_instance

    # Check if there's an existing process
    if tk_subprocess and tk_subprocess.poll() is None:
        print("Stats viewer process already running.")
        return

    # Get the absolute path to the stats data
    csv_path = _get_actual_log_path()
    if not csv_path:
        print(f"Error: Could not find stats CSV file")

        # Automatic fallback: create dummy data for demo
        csv_path = _create_dummy_log_file()
        if not csv_path:
            print("Could not create dummy file either. Cannot proceed.")
            # Force state change to avoid being stuck
            if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
                game_instance.state_manager.set_state(next_state_id_on_close)
            return None

    # Create a temporary script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stats_script_path = os.path.join(script_dir, "__temp_stats_viewer.py")

    with open(stats_script_path, 'w') as f:
        f.write("""
import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')  # Must be before other matplotlib imports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def main():
    # Get the CSV path from command line
    if len(sys.argv) < 2:
        print("Error: Missing CSV path argument")
        return 1
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return 1
    
    # Create the Tkinter window
    root = tk.Tk()
    root.title("Game Statistics")
    root.geometry("800x600")
    
    # Main container frame
    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.pack(fill="both", expand=True)
    
    # Create notebook (tabbed interface)
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True, pady=5)
    
    # Tab 1: Statistics Table
    tab_stats = ttk.Frame(notebook)
    notebook.add(tab_stats, text="Statistics")
    
    # Add refresh button to stats tab
    refresh_button = ttk.Button(tab_stats, text="Refresh Data")
    refresh_button.pack(pady=(5, 10))
    
    # Stats table
    stats_table = ttk.Treeview(tab_stats, columns=("Statistic", "Waves Reached", "Game Duration (s)"), show="headings")
    stats_table.heading("Statistic", text="Statistic")
    stats_table.heading("Waves Reached", text="Waves Reached")
    stats_table.heading("Game Duration (s)", text="Game Duration (s)")
    stats_table.column("Statistic", anchor="w", width=100)
    stats_table.column("Waves Reached", anchor="center", width=150)
    stats_table.column("Game Duration (s)", anchor="center", width=150)
    stats_table.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Tab 2: Charts
    tab_charts = ttk.Frame(notebook)
    notebook.add(tab_charts, text="Charts")
    
    # Create matplotlib figure and canvas
    fig = Figure(figsize=(8, 6), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=tab_charts)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_and_display_stats():
        # Clear previous data
        stats_table.delete(*stats_table.get_children())
        
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                tk.Label(tab_stats, text="Log file is empty.").pack(pady=10)
                return
            
            # Check and convert numeric columns
            required_cols = {'waves_reached': 'numeric', 'Time_survived_seconds': 'numeric'}
            for col, col_type in required_cols.items():
                if col not in df.columns:
                    tk.Label(tab_stats, text=f"Error: Column '{col}' not found.").pack(pady=5)
                    return
                if col_type == 'numeric':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df.dropna(subset=[col], inplace=True)
            
            if df.empty:
                tk.Label(tab_stats, text="No valid numeric data after cleaning.").pack(pady=10)
                return
            
            # Calculate statistics
            waves_stats = df['waves_reached'].agg(['min', 'max', 'mean', 'median', 'std']).fillna(0)
            duration_stats = df['Time_survived_seconds'].agg(['min', 'max', 'mean', 'median', 'std']).fillna(0)
            waves_mode = df['waves_reached'].mode()
            duration_mode = df['Time_survived_seconds'].mode()
            
            # Display in table
            stats_to_display = {
                "Min": (waves_stats.get('min', 0), duration_stats.get('min', 0)),
                "Max": (waves_stats.get('max', 0), duration_stats.get('max', 0)),
                "Mean": (f"{waves_stats.get('mean', 0):.2f}", f"{duration_stats.get('mean', 0):.2f}"),
                "Median": (waves_stats.get('median', 0), duration_stats.get('median', 0)),
                "Mode": (", ".join(map(str, waves_mode)) if not waves_mode.empty else "N/A",
                         ", ".join(map(str, duration_mode)) if not duration_mode.empty else "N/A"),
                "Std Dev": (f"{waves_stats.get('std', 0):.2f}", f"{duration_stats.get('std', 0):.2f}"),
            }
            
            for stat_name, values in stats_to_display.items():
                stats_table.insert("", "end", values=(stat_name, values[0], values[1]))
            
            # Update charts
            fig.clear()
            
            # Create two subplots for waves and duration
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212)
            
            # Waves reached histogram
            ax1.hist(df['waves_reached'], bins=10, color='skyblue', edgecolor='black')
            ax1.set_title('Waves Reached Distribution')
            ax1.set_xlabel('Waves')
            ax1.set_ylabel('Frequency')
            
            # Time survived histogram
            ax2.hist(df['Time_survived_seconds'], bins=10, color='lightgreen', edgecolor='black')
            ax2.set_title('Game Duration Distribution')
            ax2.set_xlabel('Seconds')
            ax2.set_ylabel('Frequency')
            
            fig.tight_layout()
            canvas.draw_idle()
            
        except Exception as e:
            error_text = f"An error occurred while loading stats:\\n{e}"
            tk.Label(tab_stats, text=error_text).pack(pady=10)
            print(f"Error: {e}")
    
    # Set up refresh button
    refresh_button.config(command=load_and_display_stats)
    
    # Initial data load
    load_and_display_stats()
    
    # Set up a close button to ensure clean exit
    close_button = ttk.Button(main_frame, text="Close", command=root.destroy)
    close_button.pack(pady=10)
    
    # Start the Tkinter main loop
    root.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")

    # Make a copy of the CSV data to a location that's more likely to be accessible by the subprocess
    temp_csv_path = os.path.join(os.path.dirname(
        stats_script_path), "__temp_stats_data.csv")
    try:
        shutil.copy2(csv_path, temp_csv_path)
        print(f"Copied stats data to temporary location: {temp_csv_path}")
        csv_path = temp_csv_path  # Use the copy
    except Exception as e:
        print(f"Warning: Could not copy CSV data to temporary location: {e}")
        # Continue with original path

    # Launch the process
    try:
        print(
            f"Launching stats viewer in separate process: {stats_script_path}")
        python_exe = sys.executable  # Get the current Python interpreter path
        tk_subprocess = subprocess.Popen(
            [python_exe, stats_script_path, csv_path])

        # Set up a sentinel file to detect when the process ends
        def check_process():
            if tk_subprocess.poll() is not None:
                print("Stats viewer process has ended")
                # Signal to the game to change state
                if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
                    game_instance.state_manager.set_state(
                        next_state_id_on_close)
                return False
            return True

        # This function will be called from PyGame's main loop to check process status
        return check_process

    except Exception as e:
        print(f"Error launching stats viewer process: {e}")
        # Force state change to avoid being stuck
        if 'game_instance' in globals() and hasattr(game_instance, 'state_manager'):
            game_instance.state_manager.set_state(next_state_id_on_close)
        return None


def run_stats_viewer_non_blocking(game_instance, next_state_id_on_close):
    """
    Public function to launch the Tkinter stats window in a separate thread or process.
    Does not block the main thread (PyGame).
    """
    global tk_stats_thread, tk_window_closed, tk_subprocess

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

        print("Launching Tkinter stats window in separate thread...")
        tk_stats_thread = threading.Thread(
            target=_stats_viewer_thread,
            args=(game_instance, next_state_id_on_close),
            daemon=True
        )
        tk_stats_thread.start()
        print(f"Stats viewer thread started (id: {tk_stats_thread.ident})")
        return None  # No checker needed for thread approach


def run_stats_viewer_blocking(game_instance, next_state_id_on_close):
    """
    Legacy function to launch the Tkinter stats window. Blocks execution.
    Closure of the Tkinter window triggers a state change in game_instance.

    On macOS, this will now use the process-based approach to avoid crashes.
    """
    global tk_subprocess

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
        print("Warning: Using blocking stats viewer. Consider using run_stats_viewer_non_blocking instead.")
        _stats_viewer_thread(game_instance, next_state_id_on_close)
        print("run_stats_viewer_blocking: Tkinter window closed, mainloop ended.")

    # Always ensure state change before returning
    if hasattr(game_instance, 'state_manager'):
        print(
            f"Ensuring state change to {next_state_id_on_close} before returning")
        game_instance.state_manager.set_state(next_state_id_on_close)


def close_stats_viewer():
    """
    Attempts to close an externally managed Tkinter stats window or process.
    """
    global tk_window_closed, tk_subprocess

    print("stats_viewer.close_stats_viewer() called.")

    if IS_MACOS and tk_subprocess and tk_subprocess.poll() is None:
        print("Terminating stats viewer process")
        tk_subprocess.terminate()
    else:
        tk_window_closed = True


def is_stats_viewer_open():
    """Returns True if the stats viewer is currently open."""
    global tk_stats_thread, tk_window_closed, tk_subprocess

    if IS_MACOS:
        return tk_subprocess and tk_subprocess.poll() is None
    else:
        return tk_stats_thread and tk_stats_thread.is_alive() and not tk_window_closed


if __name__ == '__main__':
    print("Running stats_viewer.py directly for testing...")

    class MockStateManager:
        def set_state(self, state_id):
            print(f"[MockStateManager] Would set state to: {state_id}")

    class MockGame:
        def __init__(self):
            self.state_manager = MockStateManager()
            print("[MockGame] Initialized.")

    mock_game = MockGame()

    print(f"LOG_GAME_CSV_PATH is configured to: {LOG_GAME_CSV_PATH}")
    actual_path_for_test = _get_actual_log_path()
    print(f"Attempting to load stats from: {actual_path_for_test}")

    if not actual_path_for_test:
        print(f"WARNING: Log file could not be located. Stats window may show an error or use a dummy.")
        # Attempt to create a dummy in a known location if all else fails
        dummy_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        dummy_path = os.path.join(
            dummy_dir, os.path.basename(LOG_GAME_CSV_PATH))
        try:
            os.makedirs(dummy_dir, exist_ok=True)
            if not os.path.exists(dummy_path):
                dummy_data = {'player_name': ['TestPlayer'], 'waves_reached': [
                    1, 2, 3, 4, 5], 'Time_survived_seconds': [10, 20, 30, 40, 50]}
                pd.DataFrame(dummy_data).to_csv(dummy_path, index=False)
                print(f"Created dummy log for testing at: {dummy_path}")
                # Point LOG_GAME_CSV_PATH to this dummy for the test
                LOG_GAME_CSV_PATH = dummy_path
            else:
                print(f"Dummy log already exists at: {dummy_path}")
        except Exception as e:
            print(f"Could not create dummy CSV for testing: {e}")

    # Based on platform, choose the appropriate approach
    print(f"Platform detected: {platform.system()}")

    if IS_MACOS:
        print("Testing on macOS - using subprocess approach...")
        check_fn = run_stats_viewer_non_blocking(
            mock_game, "TEST_MENU_STATE_AFTER_CLOSE")

        if check_fn:
            # Keep main thread alive for a while to allow viewing the window
            import time
            try:
                while check_fn():
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Test interrupted by user.")
                close_stats_viewer()
    else:
        print("Testing on Windows/Linux - using non-blocking thread mode...")
        run_stats_viewer_non_blocking(mock_game, "TEST_MENU_STATE_AFTER_CLOSE")

        # Keep main thread alive for a while to allow viewing the window
        import time
        try:
            while is_stats_viewer_open():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Test interrupted by user.")

    print("Test finished.")
