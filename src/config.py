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

# Define animation configurations based on sprite sheet columns
# Remember: Columns are 0-indexed!
ANIMATION_CONFIG = {
    # State: {animations, frames, duration_per_frame, loop?, directional?, fixed_row?}
    'idle':   {'animations': [0,1], 'duration': 0.2, 'loop': True, 'directional': True}, # Col 1,2
    'walk':   {'animations': [2,1,3],'duration': 0.15, 'loop': True, 'directional': True}, # Cols 3, 4
    'sprint': {'animations': [2,1,3], 'duration': 0.1, 'loop': True, 'directional': True}, # Cols 3,4
    'sweep': {'animations': [4,5,6,7], 'duration': 0.1, 'loop': False, 'directional': True}, # Cols 5-8
    'shoot_arrow': {'animations': [8,9,10,11], 'duration': 0.1, 'loop': False, 'directional': True}, # Future: Cols 9-12
    'cast':   {'animations': [12,13,14], 'duration': 0.1, 'loop': False, 'directional': True},# Cols 13, 14, 15
    'throw': {'animations': [15,16,17], 'duration': 0.1, 'loop': False, 'directional': True}, # Cols 16, 17, 18
    'hurt': {'animations': [18,19,20], 'duration': 0.1, 'loop': False, 'directional': True}, # Future?: Col 20 - Likely needs special handling
    'dying':  {'animations': [21,22,23], 'duration': 0.2, 'loop': False, 'directional': True}, # Cols 21-24. Assume fixed row (e.g., UP Row 4) for dying? Or use last direction? Let's try fixed row.
}

# Player configuration
PLAYER_WALK_SPEED = 90  # 1.5 * 60
PLAYER_SPRINT_SPEED = 180  # 3.0 * 60
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN = 60  # 1 per second * 60
PLAYER_SPRINT_DRAIN = 90  # 1.5 per second * 60
PLAYER_DASH_COST = 20
PLAYER_DASH_DISTANCE = 80
PLAYER_STAMINA_COOLDOWN = 2  # Cooldown period in seconds
PLAYER_RADIUS = 20
PLAYER_MAX_HEALTH = 100
PLAYER_SUMMON_LIMIT = 5
PLAYER_COLOR = BLUE  # Assuming BLUE is defined elsewhere
PLAYER_SPRITE_PATH = "sprites/player_sheet.png"
PLAYER_ANIMATION_CONFIG = ANIMATION_CONFIG

# Enemy configuration
ENEMY_BASE_HP = 50
ENEMY_BASE_SPEED = 105  # 1.75 * 60
ENEMY_DAMAGE = 5
ATTACK_COOLDOWN = 1
ENEMY_ANIMATION_CONFIG = ANIMATION_CONFIG
ENEMY_SPRITE_PATH = "sprites/enemy_sheet.png"

# File names
LOG_FILENAME = "data/log.csv"
SKILLS_FILENAME = "data/skills.csv"
