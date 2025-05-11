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
   pip install -r requirements.txt
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
```mermaid
classDiagram
        class Game {
            +player : Player
            +enemy_group : Group~Enemy~
            +state_manager : GameStateManager
            +audio : Audio
            +screen : pygame.Surface
            +clock : pygame.time.Clock
            +running : bool
            +wave_number : int
            +player_name : str
            +game_start_time : float
            +wave_start_time : float
            +current_wave_skill_usage : dict
            +current_wave_spawned_enemies : int
            +initialize_player()
            +reset_game()
            +prepare_game()
            +spawn_wave()
            +check_collisions()
            +run()
            +pause_game()
            +resume_game()
            +toggle_pause()
        }
        class Player {
            +name : str
            +deck : Deck
            +camera : Camera
            +walk_speed : float
            +sprint_speed : float
            +max_stamina : int
            +stamina : int
            +stamina_regen : float
            +sprint_drain : float
            +is_sprinting : bool
            +state : str
            +move_vector : pygame.math.Vector2
            +handle_input(dt)
            +handle_event(event, mouse_pos, enemies, now)
            +dash()
            +cast_skill(skill_idx, mouse_pos, enemies, now)
            +take_damage(amount)
            +draw(surface)
        }
        class Enemy {
            +damage : int
            +attack_cooldown : float
            +attack_timer : float
            +attack_radius : float
            +state : str
            +update(player, dt)
            +get_closest_target(player) : tuple
            +get_distance_to(other_x, other_y) : float
            +get_direction_to(target_x, target_y) : tuple
            +draw(surface)
        }
        class Entity {
            +pos : pygame.math.Vector2
            +vel : pygame.math.Vector2
            +radius : float
            +speed : float
            +max_health : int
            +health : int
            +color : tuple
            +image : pygame.Surface
            +rect : pygame.Rect
            +direction : pygame.math.Vector2
            +alive : bool
            +state : str
            +animation : CharacterAnimation
            +attack_animation_timer : float
            +attack_timer : float
            +x : float
            +y : float
            +dx : float
            +dy : float
            +move(dx, dy, dt)
            +take_damage(amount)
            +heal(amount)
            +attack(target, damage)
            +get_distance_to(other_x, other_y) : float
            +get_direction_to(target_x, target_y) : tuple
            +update_animation(dt)
            +draw(screen)
            +draw_health_bar(surface)
            +update(dt)
        }
        class Deck {
            -_skills : List~BaseSkill~
            -_projectiles : Group~ProjectileEntity~
            -_summons : Group~SummonEntity~
            +skills : List~BaseSkill~
            +projectiles : Group~ProjectileEntity~
            +summons : Group~SummonEntity~
            +get_projectiles : List~ProjectileEntity~
            +get_summons : List~SummonEntity~
            +add_skill(skill)
            +create_skills(selected_skills_data)
            +create_skill(selected_skill_data) : BaseSkill
            +use_skill(index, target_x, target_y, enemies, now, player) : bool
            +add_effect(effect)
            +update(dt, enemies)
            +draw(surface)
        }
        class Camera {
            +offset : pygame.math.Vector2
            +shake_intensity : float
            +shake_duration : float
            +shake_start_time : float
            +start_shake(intensity, duration)
            +update()
            +apply(pos) : pygame.math.Vector2
        }
        class BaseSkill {
            +name : str
            +element : str
            +skill_type : SkillType
            +cooldown : float
            +description : str
            +last_use_time : float
            +color : tuple
            +owner : Entity
            +pull : bool
            +is_off_cooldown(current_time) : bool
            +trigger_cooldown()
            +get_pull_effect(x, y, enemy)
        }
        class Projectile {
            +damage : int
            +speed : float
            +radius : float
            +duration : float
            +activate(skill, start_x, start_y, target_x, target_y) : ProjectileEntity
        }
        class Summon {
            +damage : int
            +speed : float
            +radius : float
            +duration : float
            +sprite_path : str
            +animation_config : dict
            +attack_radius : float
            +activate(skill, x, y, attack_radius) : SummonEntity
        }
        class Heal {
            +heal_amount : int
            +radius : float
            +duration : float
            +heal_summons : bool
            +activate(skill, target, summons)
        }
        class AOE {
            +damage : int
            +radius : float
            +duration : float
            +activate(skill, x, y, enemies) : bool
        }
        class Slash {
            +damage : int
            +radius : float
            +duration : float
            +activate(skill, player_x, player_y, target_x, target_y, enemies, start_angle, sweep_angle) : bool
        }
        class Chain {
            +damage : int
            +radius : float
            +duration : float
            +max_targets : int
            +chain_range : float
            +activate(skill, player_x, player_y, target_x, target_y, enemies) : List~VisualEffect~
        }
        class ProjectileEntity {
            +damage : int
            +element : str
            +explosion_radius : float
            +explosion_damage : int
            +skill_definition : Projectile
            +update(dt, enemies) : bool
            +explode(enemies) : VisualEffect
            +draw(surface)
        }
        class SummonEntity {
            +damage : int
            +element : str
            +attack_radius : float
            +update(dt, enemies) : bool
        }
        class GameStateManager {
            +game : Game
            +current_state : GameState
            +states : Dict~str, GameState~
            +overlay : GameState
            +paused : bool
            +previous_state_id : str
            +add_state(state_id, state)
            +set_state(state_id)
            +return_to_previous_state()
            +set_overlay(overlay)
            +clear_overlay()
            +pause()
            +resume()
            +toggle_pause()
            +is_paused() : bool
            +update(dt)
            +render(screen)
            +handle_events(events) : str
        }
        class GameState {
            +game : Game
            +ui_manager : UIManager
            +enter()
            +exit()
            +update(dt) : str
            +render(screen)
            +handle_events(events) : str
            +on_pause()
            +on_resume()
        }
        class MenuState {
            +title_font : pygame.font.Font
            +menu_font : pygame.font.Font
            +music_button : Button
        }
        class NameEntryState {
            +player_name : str
            +active : bool
            +input_rect : pygame.Rect
        }
        class DeckSelectionState {
            +skill_data : list
            +selected_skill_data : list
            +scroll_offset : int
            +selected_index : int
            +hamburger_button : Button
            +load_skill_data() : list
            +create_player_deck()
        }
        class PlayingState {
            +background : pygame.Surface
            +paused : bool
            +hamburger_button : Button
            +load_background()
            +setup_ui()
        }
        class StatsDisplayState {
            +is_tkinter_active : bool
        }
        class PauseOverlay {
            +resume_button : Button
            +retry_button : Button
            +quit_button : Button
            +music_button : Button
        }
        class GameOverOverlay {
            +buttons : List~Button~
            +music_button : Button
        }
        class CharacterAnimation {
            +sprite_sheet : SpriteSheet
            +config : dict
            +sprite_width : int
            +sprite_height : int
            +current_state : str
            +current_frame_index : int
            +frame_timer : float
            +current_direction_angle : int
            +animation_finished : bool
            +all_frames : list
            +set_state(new_state, force_reset)
            +update(dt, move_dx, move_dy)
            +get_current_sprite() : pygame.Surface
            +get_sprite_size() : tuple
        }
        class SpriteSheet {
            +sprite_sheet : pygame.Surface
            +get_sprite(x, y, width, height) : pygame.Surface
        }
        class VisualEffect {
            +x : float
            +y : float
            +effect_type : str
            +color : tuple
            +radius : float
            +duration : float
            +start_time : float
            +active : bool
            +alpha : int
            +current_size : float
            +start_angle : float
            +sweep_angle : float
            +angle : float
            +particles : list
            +end_x : float
            +end_y : float
            +update(dt) : bool
            +draw(surf)
        }
        class DashAfterimage {
            +original_sprite : pygame.Surface
            +duration : float
            +start_time : float
            +active : bool
            +alpha : int
            +sprite : pygame.Surface
            +is_ground_effect() : bool
        }
        class UIManager {
            +screen : pygame.Surface
            +elements : Dict~str, List~UIElement~~
            +add_element(element, group)
            +remove_element(element, group)
            +clear_group(group)
            +update(mouse_pos, dt, group)
            +update_all(mouse_pos, dt)
            +draw(group)
            +draw_all()
            +handle_event(event, group) : UIElement
        }
        class UIElement {
            +rect : pygame.Rect
            +image : pygame.Surface
            +is_hovered : bool
            +is_active : bool
            +update(mouse_pos, dt)
            +draw(screen)
            +is_clicked(mouse_pos, mouse_click) : bool
            +set_active(active)
        }
        class Button {
            +text : str
            +font : pygame.font.Font
            +color : tuple
            +hover_color : tuple
            +bg_color : tuple
            +border_color : tuple
            +draw_background : bool
            +on_click : callable
            +set_text(text)
        }
        class ProgressBar {
            +max_value : float
            +current_value : float
            +bg_color : tuple
            +fill_color : tuple
            +show_text : bool
            +label : str
            +set_value(value)
        }
        class SkillDisplay {
            +skill : BaseSkill
            +font : pygame.font.Font
            +hotkey : str
            +update_cooldown(current_time)
        }
        class StaticUIUtils {
            <<Utility>>
            +draw_selected_skills(screen, selected_skills)
            +draw_hp_bar(surface, x, y, current_hp, max_hp, bar_color)
        }
        class Audio {
            <<Singleton>>
            +current_music : str
            +music_volume : float
            +sound_effects : Dict~str, pygame.mixer.Sound~
            +sfx_volume : float
            +music_tracks : dict
            +music_enabled : bool
            +sound_enabled : bool
            +load_music()
            +play_music(music_key)
            +stop_music()
            +fade_out(fade_ms)
            +fade_in(music_key, fade_ms) : callable
            +set_music_volume(volume)
            +toggle_music() : bool
            +load_sound(name, file_path)
            +play_sound(sound_key)
            +set_sound_volume(volume)
            +toggle_sound() : bool
        }
        class FontManager {
            <<Singleton>>
            -_fonts : Dict~str, pygame.font.Font~
            -_font_path : str
            +initialize(font_path, sizes)
            +get_font(name) : pygame.font.Font
        }
        note for FontManager "Original class name: Font"
        class Config {
            <<Constants>>
            +GAME_NAME : str
            +WIDTH : int
            +HEIGHT : int
            +FPS : int
            +COLORS : dict
            +PLAYER_BASE_HP : int
            +ANIMATION_CONFIG : dict
            +SKILLS_PATH : str
            ' ... many other constants
        }
        class DataCollector {
            <<Static>>
            +current_play_id : str
            +_ensure_data_dir_exists()
            +_get_next_play_id() : str
            +initialize_csvs()
            +log_game_session_data(player_name, waves_reached, player_deck_skills, game_duration_seconds)
            +log_wave_end_data(player_name, wave_number, player_hp, player_stamina, skill_frequencies, wave_duration_seconds, spawned_enemies_count, enemies_left_count, player_deck_skills)
        }
        class Utils {
            <<Static>>
            +angle_diff(a, b) : float
            +resolve_overlap(a, b)
        }
        class StatsViewerApp {
            +game_csv_path : str
            +waves_csv_path : str
            +game_df : pandas.DataFrame
            +waves_df : pandas.DataFrame
            +root : tkinter.Tk
            +notebook : tkinter.ttk.Notebook
            +visualizations : List~Visualization~
            +load_data() : bool
            +setup_ui(root)
            +refresh_data()
            +update_visualizations()
        }
        class Visualization {
            +parent : tkinter.Widget
            +frame : tkinter.ttk.Frame
            +fig : matplotlib.figure.Figure
            +ax : matplotlib.axes.Axes
            +canvas : matplotlib.backends.backend_tkagg.FigureCanvasTkAgg
            +update(game_df, waves_df)
        }
        class SummaryStatsVisualization
        class TopPlayersVisualization
        class SkillsUsageVisualization
        class WaveHistogramVisualization
        class TopDecksVisualization
        class TimeWavesScatterVisualization

    Game "1" o-- "1" Player
    Game "1" o-- "1" GameStateManager
    Game "1" *-- "0..*" Enemy : spawns
    Game "1" o-- "1" Audio
    Game --> Config
    Game --> DataCollector
    Game --> Utils

    Player --|> Entity
    Player "1" o-- "1" Deck
    Player "1" o-- "1" Camera
    Player ..> CharacterAnimation : uses

    Enemy --|> Entity
    Enemy ..> CharacterAnimation : uses

    Entity --|> PygameSprite
    Entity ..> Config : uses
    Entity o-- CharacterAnimation : has_optional

    Deck o-- "0..*" BaseSkill : manages
    Deck o-- "0..*" ProjectileEntity : creates_and_manages
    Deck o-- "0..*" SummonEntity : creates_and_manages
    Deck o-- "0..*" VisualEffect : creates_and_manages

    Projectile --|> BaseSkill
    Summon --|> BaseSkill
    Heal --|> BaseSkill
    AOE --|> BaseSkill
    Slash --|> BaseSkill
    Chain --|> BaseSkill
    
    ProjectileEntity --|> Entity
    SummonEntity --|> Entity
    
    BaseSkill ..> Config : uses
    Projectile ..> ProjectileEntity : creates
    Summon ..> SummonEntity : creates
    Chain ..> VisualEffect : creates
    ProjectileEntity ..> VisualEffect : creates_on_explode
    SummonEntity ..> VisualEffect : creates_on_attack

    GameStateManager "1" o-- "1..*" GameState : manages
    GameStateManager ..> PauseOverlay : uses_optional
    GameStateManager ..> GameOverOverlay : uses_optional
    GameStateManager ..> Game : part_of

    GameState ..> UIManager : uses
    GameState ..> Game : part_of
    
    MenuState --|> GameState
    NameEntryState --|> GameState
    DeckSelectionState --|> GameState
    PlayingState --|> GameState
    StatsDisplayState --|> GameState
    
    PauseOverlay ..> Button : uses
    PauseOverlay ..> FontManager : uses
    PauseOverlay ..> Audio : controls

    GameOverOverlay ..> Button : uses
    GameOverOverlay ..> FontManager : uses
    GameOverOverlay ..> Audio : controls
    
    PlayingState ..> Player : updates_and_renders
    PlayingState o-- Enemy : interacts_with
    PlayingState ..> Deck : updates_and_renders
    PlayingState ..> DataCollector : logs_to
    
    DeckSelectionState ..> Deck : creates_for_player
    
    StatsDisplayState ..> StatsViewerApp : launches

    CharacterAnimation "1" o-- "1" SpriteSheet
    CharacterAnimation ..> Utils : uses
    DashAfterimage --|> VisualEffect
    VisualEffect ..> Config : uses

    UIManager o-- "0..*" UIElement : manages
    Button --|> UIElement
    ProgressBar --|> UIElement
    SkillDisplay --|> UIElement
    UIElement --|> PygameSprite
    
    SkillDisplay ..> BaseSkill : displays_info_of
    StaticUIUtils ..> FontManager : uses
    StaticUIUtils ..> Config : uses

    Audio ..> Config : uses_paths_and_settings
    FontManager ..> Config : uses_font_path
    DataCollector ..> Config : uses_paths
    DataCollector ..> BaseSkill : logs_skill_details

    StatsViewerApp o-- "0..*" Visualization : displays
    SummaryStatsVisualization --|> Visualization
    TopPlayersVisualization --|> Visualization
    SkillsUsageVisualization --|> Visualization
    WaveHistogramVisualization --|> Visualization
    TopDecksVisualization --|> Visualization
    TimeWavesScatterVisualization --|> Visualization
    StatsViewerApp ..> Config : uses_data_paths
```
- `src/`: Game engine, player, enemies, and skill classes
- `assets/`: Game assets (sprits, bgm, map, etc.)
- `data/`: Data storage for game statistics (CSV files)

## 🛠 Game Version
verion 1.0

## 👤 Creator
- Worakrit Kullanatpokin
- video [https://youtu.be/EJqSXPGo23g](https://youtu.be/rTT6APAU7Ag)

## 🤝 Credits
Sprite sheets: https://merchant-shade.itch.io/16x16-puny-characters<br/>
Map: https://merchant-shade.itch.io/16x16-puny-world<br/>
Background Music: https://www.FesliyanStudios.com
