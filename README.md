
# Incantato 🧙‍♂️

<img width="100%" alt="Screenshot 2568-04-09 at 10 06 45" src="https://github.com/user-attachments/assets/ef749a41-918e-4b93-bdfd-3b6749ad4566" />

## 🎮 What is Incantato?

**Incantato** is a fast-paced survival game where you'll:

* Build a deck of powerful elemental skills
* Fight against waves of challenging enemies
* Master strategic skill combinations

### 🏆 Your Goal
Survive as many waves as possible! Each wave becomes progressively more difficult with stronger and more numerous enemies.

### 🔑 Key Features
* **Deck Building**: Choose 4 unique skills to create your strategy
* **Wave Survival**: Test your skills against endless enemy waves
* **Resource Management**: Balance stamina usage and skill cooldowns
* **Strategic Gameplay**: Experiment with different skill combinations

## 🕹️ Game Features & Controls

| Key | Function |
|-----|----------|
| **WASD** | Move player character |
| **SHIFT** | Sprint (consumes stamina) |
| **SPACE** | Dash (consumes stamina) |
| **1-4** | Use corresponding skill from deck |
| **Mouse** | Aiming or facing direction of player|
| **ESC** | Exit game |

## 🔮 Skills

| Type | Description | How to Use | Tips |
|------------|-------------|------------|----------------|
| **Projectile** | Fast-moving attacks that travel in straight lines and deal damage on impact | Aim with mouse cursor, press corresponding skill key (1-4) to fire | Great for distant targets; aim ahead of moving enemies for better accuracy |
| **Summons** | Creates allies that automatically seek and attack nearby enemies | Press skill key to summon at your location; AI controls the summon afterward | Use to distract enemies while you reposition; effective "tanks" for drawing enemy attention |
| **AOE (Area of Effect)** | Creates expanding damage zones that affect multiple enemies within range | Aim with mouse to target location, press skill key to activate | Most effective against groups of enemies; place strategically to control enemy movement |
| **Slash** | Short-range arc attack that deals high damage directly in front of player | Face direction with mouse, press skill key to execute a quick slash attack | High damage but requires close range; combo with dash for hit-and-run tactics |
| **Chain** | Automatically targets the closest enemy and jumps to nearby targets | Press skill key to activate; automatically finds and chains between targets | Excellent against clustered enemies; no need for precise aiming |
| **Heal** | Restores player health or heals friendly summons | Press skill key to activate healing effect | Save for critical moments; most effective when health is low |

### Skill Management:
* Each skill has a **cooldown period** after use (visible on skill icons)
* Skills can be combined for powerful effects (e.g., summon allies then use AOE to protect them)
* Monitor your **stamina bar** as some skills may require stamina to cast
* Experiment with different skill combinations to find effective strategies

## 👾 Enemies

* **Orc Knight** - Deal more damange, less agile


## 📊 Data

The game records comprehensive data to help you analyze performance:
* Player statistics (waves reached, survival time)
* Skill usage patterns and effectiveness
* Cause of death analysis

> ✅ **Note:** Data analysis and visualization features will be implemented in future versions.

## ⚙️ Installation & Setup

1. **Clone Repository:**
   ```bash
   git clone https://github.com/uzimpp/incantato
   cd incantato
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Install required packages:**
   ```bash
   pip install pygame
   ```

## 🚀 Running the Game

To start the game, make sure your path is in incantato directory

run:
```bash
python src/main.py
```
When the game launches:
1. Enter your name at the prompt
2. You'll see a list of available skills - select 4 to form your deck
3. The game will begin with Wave 1 of enemies
4. Survive as long as possible!

## 🎲 Gameplay Tips

* **Deck Building:** Balance offensive and defensive skills for better survival
* **Stamina Management:** Don't deplete your stamina completely - save some for emergency dashes
* **Positioning:** Use the environment to create bottlenecks for enemies
* **Cooldown Tracking:** Keep an eye on your skill cooldowns to maximize damage output

## 📁 Project Structure
- `src/`: Game engine, player, enemies, and skill classes
- `assets/`: Game assets (sfx, bgm)
- `data/`: Data storage for game statistics (CSV files)

## 🛠 Game Version
verion 0.7

- [ ] Data visualization features will be expanded in future versions.
**(if time allows)**
- [ ] More skill types will be created in the future.
- [ ] More enemy types will be created in the future.

## 📋 Project Timeline

- 50% Checkpoint (v0.5): April 16, 2025
- Final Submission (v1.0): May 11, 2025

## 👤 Creator

- Worakrit Kullanatpokin

## 🤝 Credits
Sprite sheets: https://merchant-shade.itch.io/16x16-puny-characters<br/>
Map: https://merchant-shade.itch.io/16x16-puny-world<br/>
Background Music: https://www.FesliyanStudios.com
