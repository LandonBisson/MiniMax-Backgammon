

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

from src.utilities import create_triangle

# ----------------------------------------------------------------------------------------------------------------------

PLAYER_1_IDENTIFIER = 1
PLAYER_2_IDENTIFIER = -1


# AI Training Constants
AI_TESTING_GAMES = 25

# ----------------------------------------------------------------------------------------------------------------------

# Graphics Constants
FRAME_RATE = 60
WINDOW_WIDTH = 1250
WINDOW_HEIGHT = 750

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_DARK_GREEN = (0, 120, 0)
COLOR_DEEP_BROWN = (110, 58, 15)
COLOR_LIGHT_TAN = (236, 222, 201)
COLOR_TAN_BROWN = (171, 126, 76)
COLOR_ORANGE_BROWN =(171, 83, 10)

PLAYER_1_COLOR = COLOR_WHITE
PLAYER_2_COLOR = COLOR_BLACK

# Game Board
BOARD_CENTER_X = int(WINDOW_WIDTH / 2)
BOARD_CENTER_Y = int(WINDOW_HEIGHT / 2)
CELL_SIZE = 80 # (base of triangle)
BOX_HEIGHT_MULT = 4
HEIGHT = CELL_SIZE * BOX_HEIGHT_MULT
NUM_ROWS = 2
NUM_COLS = 12

MIDDLE_SPACE = 75
BOARD_ORIGIN_X = BOARD_CENTER_X + ((CELL_SIZE * (1 - NUM_COLS)) - MIDDLE_SPACE) / 2
BOARD_ORIGIN_Y = BOARD_CENTER_Y + ((HEIGHT / 2) * (1 - NUM_ROWS))

BOARD_WIDTH = NUM_COLS*CELL_SIZE+MIDDLE_SPACE
BOARD_HEIGHT = NUM_ROWS*HEIGHT

TRIANGLE_SHAPE = create_triangle(CELL_SIZE//2,HEIGHT//2)

TOKEN_WIDTH = 50

DICE_WIDTH = 60

NUM_TOKENS_PER_PLAYER = 15
