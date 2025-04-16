
# Incantato

<img width="674" alt="Screenshot 2568-04-09 at 10 06 45" src="https://github.com/user-attachments/assets/ef749a41-918e-4b93-bdfd-3b6749ad4566" />

## Overview
Incantato is a 2D survival wave-based game combining strategic deck-building mechanics with elemental-themed skills. Players choose and combine different elemental skills to create strategies for surviving endless waves of increasingly challenging enemies. The game focuses on strategic skill usage, stamina management, and creative tactics to reach higher waves.

## Installation

1. Clone the repository:
   ```
   git clone [your-repository-url]
   cd incantato
   ```

2. Create and activate a virtual environment:
   ```
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Game

To start the game, run:
```
python main.py
```

## Game Features

- **Elemental Deck-Building**: Players build a deck of 4 skills from different elements
- **Strategic Cooldowns**: Each skill has a cooldown period, necessitating strategic usage
- **Stamina Management**: Limited stamina requires wise resource management
- **Diverse Skill Types**: Projectiles, AOE effects, Summons, Chain effects, Slashes, and Heals
- **Endless Waves**: Gameplay scales in difficulty, testing players' strategic adaptability
- **Various Enemy Types**: Different enemy behaviors challenge different strategies

## Data Visualization

The game includes data analysis components that visualize:
- Player performance statistics (waves reached, survival time)
- Skill usage patterns and effectiveness
- Most popular skill combinations
- Cause of death analysis (HP/stamina at end of waves)
- Deck composition analysis

All visualizations are accessible through the game's statistics screen and detailed in the `screenshots/visualization` folder.

## Project Structure

- `main.py`: Main entry point for the game
- `game/`: Game engine, player, enemies, and skill classes
- `assets/`: Game assets (sprites, effects, sounds)
- `data/`: Data storage for game statistics (CSV files)
- `visualization/`: Data visualization components
- `screenshots/`: Game and visualization screenshots

## Technology Stack

- Pygame: Core game engine
- Pandas: Data processing and analysis
- Matplotlib/Seaborn: Data visualization
- NumPy: Numerical computations
- CSV: Data storage

## Data Recording

The game records data in CSV format, capturing:
- Player name and performance
- Wave statistics (HP, stamina, skill usage per wave)
- Deck compositions and effectiveness
- Enemy spawns and survival metrics

## Documentation

Full project documentation, including UML diagrams and detailed class descriptions, can be found in `DESCRIPTION.md`.

- 50% Checkpoint (v0.5): April 16, 2025
- Worakrit Kullanatpokin

## Course Information
Computer Programming II (01219116 and 01219117), 2024/2, Section 450
