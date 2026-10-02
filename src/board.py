import copy
from collections import Counter

import numpy as np

from src import constants

"""
Board is the rules and state for a turn-based game.

- State: the grid of cell values (0 = empty, non-zero = a player's identifier)
- Rules: what moves are legal, how moves are applied, and how to detect win/tie

When changing this class to create new game you must:
- Define how a move is applied and verify the move is legal
- Update the game state after each move is applied
- Define how a winner, and or tie is determined

Note: All rendering should be done elsewhere.

"""

class Board:
    def __init__(self):
        self.rows = constants.NUM_ROWS
        self.cols = constants.NUM_COLS
        # [[5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2],
        #  [-5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2]]
        self.game_board = np.array([[5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2],
                                    [-5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2]])
        # self.game_board = np.zeros((self.rows, self.cols))

        # last move as a tuple (row, col) on game_board
        self.last_move = None


    def apply_move(self, move: tuple[int, int], player_identifier) -> bool:

        """
        Try to place a player's move on the board at (row, col) specified by move.
        Returns True if move was successfully applied to the board, otherwise False.
        """

        if move[1] >= constants.NUM_COLS and self.can_score(player_identifier):
            # update score
            # if player_identifier == constants.PLAYER_1_IDENTIFIER:

            return True

        if self.is_move_valid(move,player_identifier):
            # TODO: MAKE THIS SET PLAYER JAIL SO THEN THE TURN IS DIFFERENT
            if self.game_board[move[0], move[1]] == -player_identifier:
                self.game_board[move[0], move[1]] = player_identifier
                #game_manager.current_player.in_jail = True
            else:
                self.game_board[move[0], move[1]] += player_identifier
            # if self.game_board[move[0], move[1]] == 0: #
            #     self.game_board[move[0], move[1]] = player_identifier
            self.last_move = move
            return True

        return False


    def reset(self):

        """
        Clear the game board and reset last_move for new game
        """

        self.game_board = np.array([[5,0,0,0,-3,0,-5,0,0,0,0,2],
                                    [-5,0,0,0,3,0,5,0,0,0,0,-2]])
        self.last_move = None


    def is_move_valid(self, move: tuple[int, int], player_identifier, selection: bool=False) -> bool:

        """
        Return True if the move (row, col) specified by move is valid. A move is valid if
        (row, col) is a valid index on the game board and (row, col) does not already have a move
        """
        if move is None:
            return False

        row, col = move[0], move[1]

        if col >= self.cols:
            if self.can_score(player_identifier):
                return True
            return False

        #in board
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False

        if selection and self.game_board[row][col] / player_identifier <= 0:
            return False

        #if the space isnt 0, and the piece is opposite colored, and theres only one
        if player_identifier != 0 and self.game_board[row][col] / player_identifier < 0:
            return self.game_board[row][col] == 1 or self.game_board[row][col] == -1
        # if the board spot is 0 or the player identifier that move is valid
        if self.game_board[row][col] / player_identifier >= 0:
            return True
        print("4")
        return False


    def check_winner(self) -> None|str|int:

        """
        If there are any no pieces on the board of one color they win (including no pieces in prison)
        """

        if self.last_move is None:
            return None
        player1_has_won = True
        player2_has_won = True
        for row in range(self.rows):
            for col in range(self.cols):
                if self.game_board[row][col] < 0:
                    player2_has_won = False
                if self.game_board[row][col] > 0:
                    player1_has_won = False
        if player1_has_won:
            return constants.PLAYER_1_IDENTIFIER
        elif player2_has_won:
            return constants.PLAYER_2_IDENTIFIER
        return None

    def get_game_board_in_board(self) -> np.ndarray:
        return self.game_board

    def can_score(self, identifier) -> bool:
        for row in range(self.rows):
            for col in range(self.cols):
                # player 1, overlook row 1 col 6-12, and the identifier is the same sign as the one we are looking for
                if identifier > 0 and row == 0 and col < 6 and self.game_board[row][col] != 0 and self.game_board[row][col]//abs(self.game_board[row][col]) == identifier:
                    return False
                #player 2, overlook row 2 col 6-12, and the identifier is the same sign as the one we are looking for
                elif identifier < 0 and row == 1 and col < 6 and self.game_board[row][col] != 0 and self.game_board[row][col]//abs(self.game_board[row][col]) == identifier:
                    return False

                # # player 1, overlook row 1 col 6-12, and the identifier is the same sign as the one we are looking for
                # if identifier > 0 and row == 0:
                #     return False
                # elif identifier > 0 and row == 1:
                #     if (col < 6 and self.game_board[row][col] != 0
                #             and self.game_board[row][col] // abs(self.game_board[row][col]) == identifier):
                #         return False
                #
                # # player 2, overlook row 2 col 6-12, and the identifier is the same sign as the one we are looking for
                # if identifier < 0 and row == 1:
                #     return False
                # elif identifier < 0 and row == 0:
                #     if (col < 6 and self.game_board[row][col] != 0
                #             and self.game_board[row][col] // abs(self.game_board[row][col]) == identifier):
                #         return False
        return True


    def get_possible_moves(self, dice_rolls,og_identifier) -> list[tuple[int, int]]|None:

        """
        Returns a list of all possible moves with current dice_rolls
        Could have repeat tiles in the same list because they have different starting tiles
        and rolls that make it be a repeated move spot
        """
        if dice_rolls is None:
            return None
        possible_moves = []
        for row in range(self.rows):
            for col in range(self.cols):
                if (self.game_board[row][col] == 0
                        or self.game_board[row][col] == self.game_board[row][col] // abs(self.game_board[row][col]) != og_identifier):
                    continue
                for i, roll in enumerate(dice_rolls):
                    # # if 0, or not identifier skip!
                    if not dice_rolls[i][-1]:
                        continue
                    move = None
                    if og_identifier > 0 and self.game_board[row][col] > 0:
                        if row == 0 and col - dice_rolls[i][0] < 0:
                            move = (1, abs(col - dice_rolls[i][0]) - 1, i)
                        elif row == 0:
                            move = (0, col - dice_rolls[i][0], i)
                        else:
                            move = possible_moves.append((1, col + dice_rolls[i][0], i))
                    elif og_identifier < 0 and self.game_board[row][col] < 0:
                        if row == 1 and col - dice_rolls[i][0] < 0:
                            move = (0, abs(col - dice_rolls[i][0]) - 1, i)
                        elif row == 1:
                            move = (1, col - dice_rolls[i][0], i)
                        else:
                            move = (0, col + dice_rolls[i][0], i)

                    if move is not None and self.is_move_valid(move, og_identifier):
                        possible_moves.append(move)
                        print("board iden:",self.game_board[row][col],"iden",og_identifier,"moving to:",move)
        return possible_moves

