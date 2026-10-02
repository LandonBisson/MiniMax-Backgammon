########################################################################################################################
###                                            ML MINI MAX BACKGAMMON                                                ###
########################################################################################################################
import random
from collections.abc import Sequence
from enum import Enum
from unittest import case

import pygame
from pygame import mouse # python3.12 -m src.main    to run
import numpy as np

from . import constants
from src.ai_player import AIPlayer
from src.constants import AI_TESTING_GAMES, COLOR_BLACK
from src.game_manager import GameManager, GameState
from src.human_player import HumanPlayer

from src.utilities import load_image, draw_image, draw_polygon, draw_rect_center, draw_ellipse_centered, draw_text, \
    play_music, play_sfx, draw_button, roll_dice

pygame.init()
window = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
pygame.display.set_caption('Backgammon')


# region Global Gameplay Variables -------------------------------------------------------------------------------------
# Application modes
class Mode(Enum):

    # Two AI players play against each other. No visuals are rendered to the screen.
    # Player 1 - minimax
    # Player 2 - choose random move
    TESTING_RANDOM_AI = 0

    # Two AI players play against each other. No visuals are rendered to the screen.
    # Player 1 - minimax
    # Player 2 - minimax
    TESTING_MINIMAX_AI = 1

    # One human player (player 1) and one AI player (player 2).
    # AI player will use minimax to choose best move
    HUMAN_PLAY_AI = 2

    # One human player (player 1) and one AI player (player 2).
    # AI player will choose random moves
    HUMAN_PLAY_RANDOM_AI = 3

    # Two Human players
    HUMAN_PLAY_HUMAN = 4


# Set the current mode here
mode = Mode.TESTING_MINIMAX_AI

if mode == Mode.TESTING_RANDOM_AI:
    player1 = AIPlayer(True, False)
    player2 = AIPlayer(False, True)
elif mode == Mode.TESTING_MINIMAX_AI:
    player1 = AIPlayer(True, False)
    player2 = AIPlayer(False, False)
elif mode == Mode.HUMAN_PLAY_AI:
    player1 = HumanPlayer(True)
    player2 = AIPlayer(False, False)
elif mode == Mode.HUMAN_PLAY_RANDOM_AI:
    player1 = HumanPlayer(True)
    player2 = AIPlayer(False, True)
else:
    player1 = HumanPlayer(True)
    player2 = HumanPlayer(False)

game_manager = GameManager(player1, player2)
ai_testing_games_played = 0
player_move_input = None

# images


# Reset button for Human players to restart game
reset_button = None
dice_roll_anim = 0
dice_rolls = []

# endregion ------------------------------------------------------------------------------------------------------------


def animate() -> None:
    global player_move_input
    global ai_testing_games_played
    # Update game state via game manager
    game_manager.update(player_move_input)

    # Clear any human player inputs that were applied this frame
    player_move_input = None

    # If AI is training, automatically restart next game. After all training episodes save the learned AI policy
    if (mode == Mode.TESTING_RANDOM_AI or mode == Mode.TESTING_MINIMAX_AI) and game_manager.game_state == GameState.GAME_OVER:
        ai_testing_games_played += 1
        game_manager.reset()


def paint() -> None:
    draw_game_board()
    draw_player_moves()
    draw_dice()

    if game_manager.game_state == GameState.PLAYING:
        if game_manager.is_player_one_turn():
            draw_player_one_turn()
        else:
            draw_player_two_turn()

    elif game_manager.game_state == GameState.STUCK:
        draw_stuck()

    elif game_manager.game_state == GameState.GAME_OVER:
        draw_winner()
        draw_reset_button()

def draw_game_board() -> None:
    """
    Draws the empty Tic-Tac-Toe game board. (two vertical and two horizontal lines)
    """

    triangle_colors = [constants.COLOR_LIGHT_TAN, constants.COLOR_TAN_BROWN]
    highlight_possible_moves = game_manager.get_possible_moves()
    # draws base of board brown
    draw_rect_center(window, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y), (constants.BOARD_WIDTH,constants.BOARD_HEIGHT), constants.COLOR_DEEP_BROWN,True,0)
    middle_space_x = 0
    for row in range(constants.NUM_ROWS):
        for col in range(constants.NUM_COLS):
            col_screen = constants.BOARD_ORIGIN_X + col * constants.CELL_SIZE
            row_screen = constants.BOARD_ORIGIN_Y + row * constants.HEIGHT
            #make the jump for the middle of the board
            if col > 5:
                if col == 6:
                    middle_space_x = col_screen
                col_screen += constants.MIDDLE_SPACE
            draw_polygon(window, constants.TRIANGLE_SHAPE, (col_screen, row_screen - 1), triangle_colors[col % 2],row * -180, 2, 0)

            # TRIANGLE HIGHLIGHTS AND TRIANGLES
            draw_polygon(window, constants.TRIANGLE_SHAPE, (col_screen, row_screen - 1), triangle_colors[col % 2],row * -180, 2, 0)
            # if we have possible move triangles ot highlight draw an outline
            if len(highlight_possible_moves) >= 1 and ((highlight_possible_moves[0][0] == row and highlight_possible_moves[0][1] == col)):
                draw_polygon(window, constants.TRIANGLE_SHAPE, (col_screen, row_screen - 1), constants.COLOR_YELLOW,row * -180, 2, 6)
            # draw second triangle highlight if thats another possible move
            if len(highlight_possible_moves) == 2 and (highlight_possible_moves[1][0] == row and highlight_possible_moves[1][1] == col):
                draw_polygon(window, constants.TRIANGLE_SHAPE, (col_screen, row_screen - 1), constants.COLOR_YELLOW,row * -180, 2, 6)
            #POSSIBLY DRAWING HIGHLIGHT BOXES OVER BOXES
            draw_rect_center(window, (col_screen, row_screen), (constants.CELL_SIZE, constants.HEIGHT),constants.COLOR_ORANGE_BROWN, False, 0, 2)
            if game_manager.get_selected_tile() is not None and game_manager.get_selected_tile()[0] == row and game_manager.get_selected_tile()[1] == col:
                draw_rect_center(window, (col_screen,row_screen), (constants.CELL_SIZE, constants.HEIGHT),constants.COLOR_YELLOW, False,0, 6)

    for row in range(constants.NUM_ROWS):
        col = constants.NUM_COLS+1
        col_screen = constants.BOARD_ORIGIN_X + col * constants.CELL_SIZE
        row_screen = constants.BOARD_ORIGIN_Y + row * constants.HEIGHT

        # Drawing score zones
        if len(highlight_possible_moves) >= 1 and highlight_possible_moves[0][0] == row and highlight_possible_moves[0][1] == col-1:
            draw_rect_center(window, (col_screen,row_screen), (constants.CELL_SIZE, constants.HEIGHT),constants.COLOR_YELLOW, False,0, 6)
        if len(highlight_possible_moves) == 2 and highlight_possible_moves[1][0] == row and highlight_possible_moves[1][1] == col-1:
            draw_rect_center(window, (col_screen, row_screen), (constants.CELL_SIZE, constants.HEIGHT),constants.COLOR_YELLOW, False, 0, 6)

    # print(game_manager.get_game_board())

            
    # if game_manager.player1.in_jail:
    #     draw_token(window, (middle_space_x, constants.BOARD_CENTER_Y), (constants.TOKEN_WIDTH, constants.TOKEN_WIDTH), constants.PLAYER_1_COLOR,constants.PLAYER_2_COLOR, 3)
    # elif game_manager.player2.in_jail:
    #     draw_token(window, (middle_space_x, constants.BOARD_CENTER_Y), (constants.TOKEN_WIDTH, constants.TOKEN_WIDTH),constants.PLAYER_2_COLOR, constants.PLAYER_1_COLOR, 3)

    #outlines the board
    draw_rect_center(window, (constants.BOARD_CENTER_X,constants.BOARD_CENTER_Y),(constants.BOARD_WIDTH+5,constants.BOARD_HEIGHT+5), constants.COLOR_ORANGE_BROWN,False, 0, 10)
    # draws the middle space
    draw_rect_center(window, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y),
                     (constants.MIDDLE_SPACE, constants.BOARD_HEIGHT), constants.COLOR_ORANGE_BROWN, False, 0, constants.MIDDLE_SPACE)
                     
    # Drawing Jail
    if player1.in_jail or player2.in_jail:
        if game_manager.is_current_player_in_jail():
            draw_rect_center(window, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y), (constants.CELL_SIZE, constants.BOARD_HEIGHT),constants.COLOR_YELLOW, False, 0, 6)

    # Drawing Scores
    draw_text(window, str(player1.score), 50, constants.PLAYER_1_COLOR,
              (constants.BOARD_ORIGIN_X + ((constants.NUM_COLS + 1) * constants.CELL_SIZE), constants.BOARD_ORIGIN_Y + constants.HEIGHT))
    # print("Player 1 score", player1.score)
    draw_text(window, str(player2.score), 50, constants.PLAYER_2_COLOR,
              (constants.BOARD_ORIGIN_X + ((constants.NUM_COLS + 1) * constants.CELL_SIZE), constants.BOARD_ORIGIN_Y))

   

def draw_dice() -> None:
    global dice_rolls,dice_roll_anim
    #dice_rolls is set to one of these values when we click the roll, otherwise we want to just draw random dice
    if dice_rolls is not None:
        past_roll = dice_rolls
    dice_rolls = game_manager.get_dice_rolls()
    # set the starting point
    starting_y_shift = constants.DICE_WIDTH/2
    #draw random dice
    dice_roll_anim += 1
    if dice_rolls is None or len(dice_rolls) == 0:
        #this is purely for a cosmetic roll, but we dont want to show doubling
        if dice_roll_anim % 5 == 0:
            dice_rolls = [[random.randint(1, 6), True],[random.randint(1, 6),True]]
        # sustain the past roll
        else:
            dice_rolls = past_roll

    # draw real dice (condition of dice_rolls can change because of the animate)
    if dice_rolls is not None:
        #shift starting point if there is four dice
        if len(dice_rolls) == 4:
            starting_y_shift = int(constants.DICE_WIDTH * 2)
        for i in range(len(dice_rolls)):
            if dice_rolls[i][1]:
                dice_x_pos = constants.BOARD_CENTER_X * .085
                dice_y_pos = int(constants.BOARD_CENTER_Y + starting_y_shift - (constants.DICE_WIDTH * i * 1.1))
                # draw dice white base
                draw_rect_center(window, (dice_x_pos, dice_y_pos),(constants.DICE_WIDTH, constants.DICE_WIDTH), constants.COLOR_WHITE, False, 0, 0)
                #draw pips
                draw_dice_pips(dice_x_pos,dice_y_pos,constants.DICE_WIDTH,dice_rolls[i][0])

def draw_dice_pips(center_x,center_y,dice_width, dice):
    pip_size = dice_width // 3
    pip_shift = pip_size//1.1
    # make it a tuple of x and y because pips will always be circles
    pip_size = (pip_size,pip_size)
    match dice:
        case 1:
            # window: pygame.surface, center: tuple[int,int], size: tuple[int,int], color, fill : bool = False, border_width = 0
            draw_ellipse_centered(window,(center_x,center_y),pip_size,constants.COLOR_BLACK,True)
        case 2:
            draw_ellipse_centered(window,(center_x - pip_shift,center_y - pip_shift),pip_size,constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x + dice_width // 3, center_y + dice_width // 3), pip_size,constants.COLOR_BLACK, True)
        case 3:
            draw_ellipse_centered(window, (center_x - pip_shift, center_y - pip_shift), pip_size,constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x, center_y), pip_size, constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y + pip_shift), pip_size,constants.COLOR_BLACK, True)
        case 4:
            draw_ellipse_centered(window, (center_x - pip_shift, center_y - pip_shift), pip_size,constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x - pip_shift, center_y + pip_shift), pip_size,constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y - pip_shift), pip_size,constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y + pip_shift), pip_size,constants.COLOR_BLACK, True)
        case 5:
            draw_ellipse_centered(window, (center_x - pip_shift, center_y - pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x - pip_shift, center_y + pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x, center_y), pip_size, constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y - pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y + pip_shift), pip_size, constants.COLOR_BLACK,True)
        case 6:
            draw_ellipse_centered(window, (center_x - pip_shift, center_y - pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x - pip_shift, center_y + pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y - pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y + pip_shift), pip_size, constants.COLOR_BLACK,True)
            draw_ellipse_centered(window, (center_x - pip_shift, center_y), pip_size, constants.COLOR_BLACK, True)
            draw_ellipse_centered(window, (center_x + pip_shift, center_y), pip_size, constants.COLOR_BLACK, True)

def draw_player_moves() -> None:
    """
    Draw all moves from both players on the board.
    """

    # Convert board coordinates (row, col) into screen coordinates for drawing.
    # The board is centered at (BOARD_CENTER_X, BOARD_CENTER_Y).
    for row in range(constants.NUM_ROWS):
        for col in range(constants.NUM_COLS+1):

            players_on_curr_tile = game_manager.get_game_board()[row][col]
            if players_on_curr_tile == 0: # Continue if no players on this tile
                continue

            if col >= constants.NUM_COLS and (player1.in_jail or player2.in_jail): # Draw players in jail
                
                jail_height = constants.BOARD_HEIGHT // 3
                col_screen = constants.BOARD_CENTER_X
                row_screen = constants.BOARD_CENTER_Y + row * constants.HEIGHT

                color = constants.PLAYER_2_COLOR if players_on_curr_tile < 0 else constants.PLAYER_1_COLOR
                opposite_color = constants.PLAYER_1_COLOR if players_on_curr_tile < 0 else constants.PLAYER_2_COLOR
                base_fit_in_tile = 4
                if players_on_curr_tile != 0:
                    distance_between_piece = (jail_height - constants.TOKEN_WIDTH) / players_on_curr_tile
                if row == 0:
                    piece_y_screen = row_screen - jail_height
                else:
                    piece_y_screen = row_screen - (constants.HEIGHT - jail_height)

                for i in range(int(abs(players_on_curr_tile))):
                    draw_token(window, (col_screen, piece_y_screen),(constants.TOKEN_WIDTH, constants.TOKEN_WIDTH), color,opposite_color, 3)
                    if abs(players_on_curr_tile) > base_fit_in_tile:
                        if row == 0:
                            piece_y_screen += distance_between_piece * (abs(players_on_curr_tile)/players_on_curr_tile)
                        else:
                            piece_y_screen -= distance_between_piece * (abs(players_on_curr_tile) / players_on_curr_tile)
                    else:
                        if row == 0:
                            piece_y_screen += constants.TOKEN_WIDTH
                        else:
                            piece_y_screen -= constants.TOKEN_WIDTH
                
                continue


            col_screen = constants.BOARD_ORIGIN_X + col * constants.CELL_SIZE
            row_screen = constants.BOARD_ORIGIN_Y + row * constants.HEIGHT
            # make the jump for the middle of the board
            if col > 5:
                col_screen += constants.MIDDLE_SPACE

            #these colors should be overwritten
            color = constants.PLAYER_2_COLOR if players_on_curr_tile < 0 else constants.PLAYER_1_COLOR
            opposite_color = constants.PLAYER_1_COLOR if players_on_curr_tile < 0 else constants.PLAYER_2_COLOR
            # this is how many can fit in a tile
            base_fit_in_tile = 6
            # calculate the step size for the pieces evenly spaced on the board
            if players_on_curr_tile != 0:
                distance_between_piece = (constants.HEIGHT - constants.TOKEN_WIDTH) / players_on_curr_tile
            # figure out if we need to start at the bottom or top
            if row == 0:
                piece_y_screen = row_screen - constants.HEIGHT // 2 + constants.TOKEN_WIDTH // 2 + 10
            else:
                piece_y_screen = row_screen + constants.HEIGHT / 2 - constants.TOKEN_WIDTH / 2 - 10

            for i in range(int(abs(players_on_curr_tile))):
                draw_token(window, (col_screen, piece_y_screen),(constants.TOKEN_WIDTH, constants.TOKEN_WIDTH), color,opposite_color, 3)
                if abs(players_on_curr_tile) > base_fit_in_tile:
                    if row == 0:
                        piece_y_screen += distance_between_piece * (abs(players_on_curr_tile)/players_on_curr_tile)
                    else:
                        piece_y_screen -= distance_between_piece * (abs(players_on_curr_tile) / players_on_curr_tile)
                else:
                    if row == 0:
                        piece_y_screen += constants.TOKEN_WIDTH
                    else:
                        piece_y_screen -= constants.TOKEN_WIDTH

def draw_token(window: pygame.surface, center: tuple[int,int], size: tuple[int,int], color,opposite_color, border_width = 0, highlight = False) -> None:
    draw_ellipse_centered(window, center, (constants.TOKEN_WIDTH, constants.TOKEN_WIDTH), color,True)
    draw_ellipse_centered(window, center, size,opposite_color, False, border_width)
    # draw_text(window, "", 25, opposite_color, center)

def draw_player_one_turn() -> None:
    draw_text(window, "Player One", 25, constants.PLAYER_1_COLOR, (int(constants.WINDOW_WIDTH * 0.07), 10))


def draw_player_two_turn() -> None:
    draw_text(window, "Player Two", 25, constants.PLAYER_2_COLOR, (int(constants.WINDOW_WIDTH * 0.93), 10))

def draw_stuck() -> None:
    if game_manager.current_player == game_manager.player1:
        color = constants.PLAYER_1_COLOR
    else:
        color = constants.PLAYER_2_COLOR

    draw_text(window, "No Possible Moves!", 50, color, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y-30))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.event.clear()
    game_manager.switch_turn()

def draw_winner() -> None:
    if game_manager.player_one_won():
        winner_text = "Player One Wins!"
        color = constants.PLAYER_1_COLOR
    elif game_manager.player_two_won():
        winner_text = "Player Two Wins!"
        color = constants.PLAYER_2_COLOR
    else:
        winner_text = "Tie!"
        color = constants.COLOR_WHITE

    draw_text(window, winner_text, 50, color, (constants.BOARD_CENTER_X, constants.BOARD_CENTER_Y-30))

def draw_reset_button() -> None:
    global reset_button
    reset_button = draw_button(window, "Reset", (int(constants.WINDOW_WIDTH * 0.5), constants.WINDOW_HEIGHT - 30), 20,
                               constants.COLOR_RED, constants.COLOR_GREEN)
# region User Input ----------------------------------------------------------------------------------------------------
def process_mouse_event(event: pygame.event.Event) -> None:
    """
    This method is called when a mouse event occurs.

    :param event: The Pygame mouse event to process (MOUSEBUTTONDOWN, or MOUSEMOTION)
    """

    global player_move_input, reset_button, stuck_button

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if game_manager.game_state == GameState.GAME_OVER:
            if reset_button is not None and reset_button.collidepoint(event.pos):
                game_manager.reset()

        elif game_manager.game_state == GameState.PLAYING:
            x_pos, y_pos = mouse.get_pos()
            player_move_input = x_pos, y_pos
            # print("~~~~", player_move_input)

def process_key_event(event: pygame.event.Event) -> None:
    """
    This method is only called when a key event occurs.

    :param event: The Pygame key KEYDOWN event to process
    """
    pass

def process_keys_held(keys: Sequence[bool]) -> None:
    """
    This method is called every frame. Used to get keys that are held over sequential frames
    :param keys:
    :return:
    """
    pass


# endregion

# region Game Update Loop ----------------------------------------------------------------------------------------------

def reset() -> None:
    # pass is what we put in a function when we have not implemented it yet.
    # After you add code to this method, delete the pass line of code.
    global dice_roll_anim, dice_rolls
    dice_roll_anim = 0
    dice_rolls = []


########################################################################################################################
# You should not have to edit any of the code in the game update loop below
########################################################################################################################

def play_game():
    reset()

    # If training in headless mode then no rendering (pygame) is needed
    if mode == Mode.TESTING_RANDOM_AI or mode == Mode.TESTING_MINIMAX_AI:
        while ai_testing_games_played < AI_TESTING_GAMES:
            animate()
        return


    run = True
    frame_rate = int(constants.FRAME_RATE)
    frame_rate = frame_rate if frame_rate > 0 else 15
    while run:

        # Limit the game to FRAME_RATE frames per second (delay in milliseconds).
        pygame.time.delay(int(1000 / frame_rate))

        # Handle all events from the previous frame.
        # Quit event - exit game loop
        # Mouse events: pass to mouse event input handler
        # Key events: pass to keyboard even input handler
        pygame_events = pygame.event.get()
        for pygame_event in pygame_events:
            if pygame_event.type == pygame.QUIT:
                run = False
            else:
                if pygame_event.type == pygame.MOUSEBUTTONDOWN or pygame_event.type == pygame.MOUSEBUTTONUP or pygame_event.type == pygame.MOUSEMOTION:
                    process_mouse_event(pygame_event)

                if pygame_event.type == pygame.KEYDOWN or pygame_event.type == pygame.KEYUP:
                    process_key_event(pygame_event)

        # Keys held: pass to keys held input handler
        process_keys_held(pygame.key.get_pressed())

        # Update the game state (position, collisions, and timers)
        window.fill(constants.COLOR_DARK_GREEN)
        animate()

        # Render visuals
        paint()

        pygame.display.update()

    pygame.quit()


# endregion

if __name__ == '__main__':
    play_game()
