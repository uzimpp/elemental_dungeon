
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
            error_text = f"An error occurred while loading stats:\n{e}"
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
