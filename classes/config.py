#  Author: Gordei Ussatsov
#  Date: 08 April 2019
#  Version: 3.0
#  Game Configs
from pathlib import Path

# ----------SpritesFolders----------
RESOURCE_DIR = Path(__file__).absolute().parent.parent / 'resources'
EXPLOSIONS_DIR = RESOURCE_DIR / 'explosions'
LANDING_PADS_DIR = RESOURCE_DIR / 'landingPads'
METEORS_DIR = RESOURCE_DIR / 'meteors'
OBSTACLE_FOLDER = RESOURCE_DIR / 'obstacles'
SHIP_EXPLOSION = RESOURCE_DIR / 'ship_explosion'
SOUND_EFFECTS = RESOURCE_DIR / 'soundEffects'
BACKGROUND_DIR = RESOURCE_DIR / 'background'
SHIP_DIR = RESOURCE_DIR / 'ship'

# ----------Window----------
TITLE = "Mars Lander"
WIDTH = 1200
HEIGHT = 750
FPS = 120
GRAVITY = .002
HEIGTADJUSTMENT = 4/3

# ----------Player----------
LANDING_POINTS = 50

# ----------Sound----------
ALLERTSOUND = "allert_sound.wav"
METEOR_EXPLOSION = {"explosion1.wav", "explosion2.wav"}
BGMUSIC = "dark fallout.ogg"

# ----------Ship----------
NOTTHRUSTINGSHIP = "lander.png"
THRUSTINGSHIP = "thrust.png"
SHIP_ROT_SPEED = .5

# ----------Engine----------
ENGINE_ACC = .01

# ----------Obstacles----------
OBSTICLEDMG = 0

# ----------Meteors----------
METEORDMG = 0

# ----------Colors----------
BLACK = (0, 0, 0)
GREEN = (124, 252, 0)
WHITE = (255, 255, 255)
