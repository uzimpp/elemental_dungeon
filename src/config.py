"""
Module containing all configuration constants for the game.
"""


class Config:
    """
    Configuration class containing all game settings and constants.

    Includes screen dimensions, colors, game balance values, animation settings,
    entity properties, and file paths needed throughout the game.
    """
    # Game Name
    GAME_NAME = "Incantato"
    VISUALIZE_NAME = "Data Visualizer of Incantato"

    # Screen constants
    WIDTH = 1280
    HEIGHT = 720
    FPS = 60
    SKILLS_LIMIT = 4
    FONT_SIZES = {
        'TITLE': 48,
        'MENU': 32,
        'SKILL': 24,
        'DESC': 18,
        'UI': 16
    }
    # Basic colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_GREY = (200, 200, 200)
    GREY = (128, 128, 128)
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
    WAVE_MULTIPLIER = 0.1
    PLAYER_BASE_HP = 100
    ENEMY_BASE_HP = 50
    PLAYER_BASE_SPEED = 64  # 1 * 60
    PLAYER_SPRINT_SPEED = 192  # 3.0 * 60
    ENEMY_BASE_SPEED = 112  # 1.75 * 60
    SPRITE_SIZE = 32
    RENDER_SIZE = 64
    ATTACK_COOLDOWN = 1.25
    ATTACK_RADIUS = 96
    PULL_STRENGTH = 48

    # Animation configurations for sprite sheets
    ANIMATION_CONFIG = {
        'idle': {
            'animations': [0, 1],
            'duration': 0.2,
            'loop': True,
            'directional': True
        },
        'walk': {
            'animations': [2, 1, 3],
            'duration': 0.15,
            'loop': True,
            'directional': True
        },
        'sprint': {
            'animations': [2, 1, 3],
            'duration': 0.1,
            'loop': True,
            'directional': True
        },
        'sweep': {
            'animations': [4, 5, 6, 7],
            'duration': 0.1,
            'loop': False,
            'directional': True
        },
        'shoot_arrow': {
            'animations': [8, 9, 10, 11],
            'duration': 0.1,
            'loop': False,
            'directional': True
        },
        'cast': {
            'animations': [12, 13, 14],
            'duration': 0.1,
            'loop': False,
            'directional': True
        },
        'throw': {
            'animations': [15, 16, 17],
            'duration': 0.1,
            'loop': False,
            'directional': True
        },
        'hurt': {
            'animations': [18, 19, 20],
            'duration': 0.1,
            'loop': False,
            'directional': True
        },
        'dying': {
            'animations': [21, 22, 23],
            'duration': 0.3,
            'loop': False,
            'directional': True
        },
    }

    # Player configuration
    PLAYER_WALK_SPEED = 90  # 1.5 * 60
    PLAYER_SPRINT_SPEED = 180  # 3.0 * 60
    PLAYER_MAX_STAMINA = 100
    PLAYER_STAMINA_REGEN = 15
    PLAYER_SPRINT_DRAIN = 20
    PLAYER_DASH_COST = 30
    PLAYER_DASH_DISTANCE = 128
    PLAYER_STAMINA_COOLDOWN = 2.5
    PLAYER_RADIUS = RENDER_SIZE / 3
    PLAYER_MAX_HEALTH = 100
    PLAYER_SUMMON_LIMIT = 5
    PLAYER_COLOR = BLUE
    PLAYER_SPRITE_PATH = "assets/sprites/player_sheet.png"
    PLAYER_ANIMATION_CONFIG = ANIMATION_CONFIG

    # Enemy configuration
    ENEMY_BASE_HP = 50
    ENEMY_BASE_SPEED = 105  # 1.75 * 60
    ENEMY_DAMAGE = 5
    ENEMY_RADIUS = RENDER_SIZE / 3
    ENEMY_ANIMATION_CONFIG = ANIMATION_CONFIG
    ENEMY_SPRITE_PATH = "assets/sprites/enemy_sheet.png"
    ENEMY_COLOR = RED

    SHADOW_SUMMON_ANIMATION_CONFIG = ANIMATION_CONFIG
    SHADOW_SUMMON_SPRITE_PATH = "assets/sprites/shadow_summon_sheet.png"
    WOOD_SUMMON_ANIMATION_CONFIG = ANIMATION_CONFIG
    WOOD_SUMMON_SPRITE_PATH = "assets/sprites/wood_summon_sheet.png"

    # File names
    GAMES_LOG_PATH = "data/games.csv"
    WAVES_LOG_PATH = "data/waves.csv"
    SKILLS_PATH = "data/skills.csv"
    MENU_BGM_PATH = "assets/music/menu.mp3"
    GAME_BGM_PATH = "assets/music/retro-forest.mp3"
    FONT_PATH = "assets/fonts/PixelifySans-Regular.ttf"
    MAP_PATH = "assets/map/map.png"
