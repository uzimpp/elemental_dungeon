# Game Name
GAME_NAME = "Incantato"

# Screen constants
WIDTH = 1028
HEIGHT = 720
FPS = 60

# Basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Element colors with both primary and accent variants
ELEMENT_COLORS = {
    'FIRE': {
        'primary': (255, 80, 0),    # Bright orange
        'accent': (255, 160, 30)    # Light orange
    },
    'WATER': {
        'primary': (0, 80, 255),    # Deep blue
        'accent': (30, 144, 255)    # Light blue
    },
    'ICE': {
        'primary': (135, 206, 235),  # Sky blue
        'accent': (176, 224, 230)   # Powder blue
    },
    'WIND': {
        'primary': (200, 200, 200),  # Light gray
        'accent': (220, 220, 255)   # Light blue-white
    },
    'WOOD': {
        'primary': (34, 139, 34),   # Forest green
        'accent': (50, 205, 50)     # Lime green
    },
    'ROCK': {
        'primary': (139, 69, 19),   # Brown
        'accent': (160, 82, 45)     # Sienna
    },
    'THUNDER': {
        'primary': (255, 215, 0),   # Golden yellow
        'accent': (255, 255, 100)   # Bright yellow
    },
    'SHADOW': {
        'primary': (80, 0, 80),     # Dark purple
        'accent': (128, 0, 128)     # Purple
    },
    'LIGHT': {
        'primary': (255, 223, 186),  # Light peach
        'accent': (255, 236, 179)   # Pale yellow
    },
    'SOUND': {
        'primary': (138, 43, 226),  # Blue violet
        'accent': (147, 112, 219)   # Medium purple
    }
}

# UI colors
UI_COLORS = {
    'hp_bar_bg': (60, 60, 60),
    'hp_bar_fill': (50, 220, 50),
    'hp_text': (255, 255, 255),
    'stamina_bar_bg': (60, 60, 60),
    'stamina_bar_fill': (220, 220, 0),
    'stamina_text': (255, 255, 255),
    'skill_box_bg': (40, 40, 40),
    'cooldown_overlay': (0, 0, 0, 128),
    'skill_text': (255, 255, 255),
    'skill_hotkey': (200, 200, 200),
}

# Game balance constants
WAVE_MULTIPLIER = 0.2
PLAYER_BASE_HP = 100
ENEMY_BASE_HP = 50
PLAYER_BASE_SPEED = 60  # 1 * 60
PLAYER_SPRINT_SPEED = 180  # 3.0 * 60
ENEMY_BASE_SPEED = 105  # 1.75 * 60
SPRITE_SIZE = 32
RENDER_SIZE = WIDTH // 16
ATTACK_COOLDOWN = 1.25
ATTACK_RADIUS = 32


# Player configuration
PLAYER_WALK_SPEED = 90  # 1.5 * 60
PLAYER_SPRINT_SPEED = 180  # 3.0 * 60
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN = 30
PLAYER_SPRINT_DRAIN = 80
PLAYER_DASH_COST = 50
PLAYER_DASH_DISTANCE = 100
PLAYER_STAMINA_COOLDOWN = 2.5  # Cooldown period in seconds
PLAYER_RADIUS = RENDER_SIZE / 3
PLAYER_MAX_HEALTH = 100
PLAYER_SUMMON_LIMIT = 5
PLAYER_SPRITE_PATH = "assets/sprites/player_sheet.png"

# Enemy configuration
ENEMY_BASE_HP = 50
ENEMY_BASE_SPEED = 105  # 1.75 * 60
ENEMY_DAMAGE = 5
ENEMY_RADIUS = RENDER_SIZE / 3
ENEMY_SPRITE_PATH = "assets/sprites/enemy_sheet.png"

SHADOW_SUMMON_SPRITE_PATH = "assets/sprites/shadow_summon_sheet.png"

# File names
LOG_PATH = "data/log.csv"
SKILLS_PATH = "data/skills.csv"
MENU_BGM_PATH = "assets/music/menu.mp3"
GAME_BGM_PATH = "assets/music/retro-forest.mp3"
