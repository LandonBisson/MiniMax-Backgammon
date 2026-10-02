from src import constants
from src.board import Board
from enum import Enum

from src.utilities import move_within_bounds, roll_dice

"""
game_manager.py

GameManager runs the turn-based game loop logic (NOT the pygame loop).

Responsibilities:
- Owns the Board and the two Player objects
- Tracks whose turn it is
- Asks the current player to choose a move
- Applies the move to the board (using board.apply_move)
- Checks for a winner/tie after each valid move
- Switches turns when the game continues
- During AI training: records AI states and feeds rewards when the game ends

Important:
- GameManager contains no rendering or pygame code.
- Player objects only CHOOSE moves. GameManager applies moves and advances the game.
"""


# stage 0 is dice roll, stage 1 is selecting the piece you want to move, stage 2 is selecting the place that piece would move to
current_stage = 0
select_tile = None
move_tile = None
dice_rolls = None
possible_moves = []

class GameState(Enum):
    PLAYING = 0     # game is active, moves are still being applied
    GAME_OVER = 1   # a player has won the game, or game ended in a tie
    RESET = 2       # waiting to reset (waiting to start a new game)


class GameManager:

    def __init__(self, player1, player2):
        self.board = Board()

        # players can either be Human or AI players
        self.player1 = player1
        self.player2 = player2

        self.current_player = self.player1
        self.game_state = GameState.PLAYING


    def update(self, pending_move):

        """
        Advance the game by at most ONE move.

        pending_move: Human player only - (x, y) mouse click pixels

        Each move follows the following rules:
        1. Ask the current player to choose a move
        2. Apply the chosen move to the board
        3. If move was valid:
            - If current player is AI player record the move state
            - Check for game over (winner or tie)
            - If game over:
                - AI players feed reward
                - restart game
            - If not game over then set current player to other player

        """
        global current_stage, dice_rolls, possible_moves, select_tile, move_tile

        if self.game_state != GameState.PLAYING:
            return
        #convert pending move into a board space
        if self.current_player.is_ai_player:
            chosen_move = self.current_player.choose_move(self.board, dice_rolls)
        else:
            chosen_move = self.current_player.choose_move(self.board, pending_move)
        #dice need to roll
        if current_stage == 0:
            if move_within_bounds(pending_move,(constants.BOARD_CENTER_X*.085, constants.BOARD_CENTER_Y),
                                  (constants.DICE_WIDTH,constants.DICE_WIDTH)) or self.current_player.is_ai_player:
                dice_rolls = roll_dice()
                print("DICE:",dice_rolls)
                current_stage += 1
        elif (current_stage == 1 and
              self.board.is_move_valid(chosen_move, self.current_player.identifier, not self.current_player.is_ai_player)):
            # print("Stage", current_stage)
            #pick token
            current_stage += 1
            select_tile = chosen_move
        #pick select tile
        elif current_stage == 2 and self.current_player.is_ai_player:
                if dice_rolls[chosen_move[-1]][-1]:

                    # print("Removed 1 dice:",dice_rolls)
                    # gets rid of the piece the player was on
                    remove_move = self.current_player.get_the_remove_the_select_move(dice_rolls,chosen_move[-1],(chosen_move[0],chosen_move[1]),self.current_player.identifier)
                    #applies the new piece move
                    if self.board.apply_move(chosen_move, self.current_player.identifier):
                        # DICE HAS BEEN USED (after we calc remove move correct)
                        dice_rolls[chosen_move[-1]][-1] = False
                        print("Chosen move", chosen_move, "remove_move", remove_move)
                        if remove_move is not None:
                            self.board.game_board[remove_move[0]][remove_move[1]] -= self.current_player.identifier

                        if self.board.check_winner() is not None:
                            self.game_state = GameState.GAME_OVER
                        no_more_dice = True
                        for i in range(len(dice_rolls)):
                            if dice_rolls[i][-1]:
                                no_more_dice = False
                                current_stage = 1
                                break
                        if no_more_dice:
                            # resets everything for the next players turn
                            self.current_player = self.player2 if self.current_player == self.player1 else self.player1
                            dice_rolls = None
                            chosen_move = None
                            select_tile = None
                            current_stage = 0

        elif current_stage == 2:
            # if you pressed on the same tile as the select tile, restart the selection process
            if chosen_move == select_tile:
                # setting select tile to none gets rid of the board highlight, and to allow re-selections
                select_tile = None
                move_tile = None
                possible_moves = []
                current_stage = 1
                return
            #build possible moves
            for i in range(len(dice_rolls)):
                # would fall off the dge o the board
                if not dice_rolls[i][-1]:
                    continue
                if len(possible_moves) < 2:
                    move = None

                    identifier = int((self.current_player.identifier + 1) / 2)  # will get 0 and 1 for black and white respectively
                    if select_tile[0] == abs(identifier - 1) and select_tile[1] - dice_rolls[i][0] < 0:
                        move = (identifier, abs(select_tile[1] - dice_rolls[i][0])-1)
                    elif select_tile[0] == abs(identifier - 1):
                        move = (abs(identifier - 1), select_tile[1] - dice_rolls[i][0])
                    else:
                        col = select_tile[1] + dice_rolls[i][0]
                        if col > constants.NUM_COLS:
                            move = (identifier, constants.NUM_COLS)
                        else:
                            move = (identifier, select_tile[1] + dice_rolls[i][0])

                    if move is not None and self.board.is_move_valid(move, self.current_player.identifier):
                        possible_moves.append((move[0], move[1], i))

            # print("possible moves:",possible_moves)

            # check to see if the possible moves are the chosen move, then make that the select tile.
            for i in range(len(possible_moves)):
                if (possible_moves[i][0],possible_moves[i][1]) == chosen_move and dice_rolls[possible_moves[i][-1]][-1]:
                    # DICE HAS BEEN USED
                    dice_rolls[possible_moves[i][-1]][-1] = False
                    # print("Removed 1 dice:",dice_rolls)
                    move_tile = chosen_move
                    # gets rid of the piece the player was on
                    self.board.game_board[select_tile[0]][select_tile[1]] -= self.current_player.identifier
                    #applies the new piece move
                    if self.board.apply_move(move_tile, self.current_player.identifier):
                        if self.board.check_winner() is not None:
                            self.game_state = GameState.GAME_OVER

                        no_more_dice = True
                        for i in range(len(dice_rolls)):
                            if dice_rolls[i][-1]:
                                no_more_dice = False
                                current_stage = 1
                                select_tile = None
                                move_tile = None
                                possible_moves = []
                                break
                        if no_more_dice:
                            # resets everything for the next players turn
                            self.current_player = self.player2 if self.current_player == self.player1 else self.player1
                            current_stage = 1
                            select_tile = None
                            move_tile = None
                            possible_moves = []
                            dice_rolls = None
                            current_stage = 0
                    break
            # then make the switch
            # get the tile you are moving to
        #see if all the dice are used
        else:
            if dice_rolls is None:
                current_stage = 0
            else:
                current_stage = 1

    def update_ai_player_testing_diagnostics(self, winning_player_identifier):
        if winning_player_identifier == "Tie":
            if self.player1.is_ai_player:
                self.player1.update_testing_diagnostics("ties")
            if self.player2.is_ai_player:
                self.player2.update_testing_diagnostics("ties")
        elif winning_player_identifier == self.player1.identifier:
            if self.player1.is_ai_player:
                self.player1.update_testing_diagnostics("wins")
            if self.player2.is_ai_player:
                self.player2.update_testing_diagnostics("losses")
        elif winning_player_identifier == self.player2.identifier:
            if self.player1.is_ai_player:
                self.player1.update_testing_diagnostics("losses")
            if self.player2.is_ai_player:
                self.player2.update_testing_diagnostics("wins")

    def get_possible_moves(self):
        return possible_moves
    def get_selected_tile(self):
        return select_tile
    def get_dice_rolls(self):
        return dice_rolls
    def is_player_one_turn(self):
        return self.current_player == self.player1

    def is_player_two_turn(self):
        return self.current_player == self.player2

    def player_one_won(self):
        winner = self.board.check_winner()
        return winner == self.player1.identifier

    def player_two_won(self):
        winner = self.board.check_winner()
        return winner == self.player2.identifier

    def reset(self):

        """
        Reset the game back to a fresh starting state.

        - Clears the board
        - Sets the turn back to player1
        - Returns the game to PLAYING
        """

        self.board.reset()
        self.game_state = GameState.PLAYING
        self.current_player = self.player1

        global current_stage, select_tile, dice_rolls, possible_moves, select_tile, move_tile
        current_stage = 0
        select_tile = None
        move_tile = None
        dice_rolls = None
        possible_moves = []

    def get_game_board(self):
        return self.board.get_game_board_in_board()


    def current_player(self):
        return self.current_player

