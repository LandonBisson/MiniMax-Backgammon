import copy
from collections import Counter

import numpy as np

from . import constants

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
        #  [-5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2]]                             Jail (-2)   Goal (-1)
        self.game_board = np.array([[5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2,         0,          0],
                                    [-5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2,         0,          0]])

        # self.game_board = np.zeros((self.rows, self.cols))
        # self.game_board = np.zeros((self.rows, self.cols))

        # last move as a tuple (row, col) on game_board
        self.last_move = None


    def apply_move(self, move: tuple[int, int], player_identifier) -> bool:

        """
        Try to place a player's move on the board at (row, col) specified by move.
        Returns True if move was successfully applied to the board, otherwise False.
        """

        # Scoring
        if move[1] >= constants.NUM_COLS and self.can_score(player_identifier):
            
            self.game_board[move[0], -1] += abs(player_identifier)

            return True

        if self.is_move_valid(move,player_identifier):

            ########################################################################
            # TODO: MAKE THIS SET PLAYER JAIL SO THEN THE TURN IS DIFFERENT
            ########################################################################

            if self.game_board[move[0], move[1]] == -player_identifier:
                self.game_board[move[0], move[1]] = player_identifier
                identifier = int((player_identifier + 1) / 2) # 1 for player 1, 0 for player 2
                self.game_board[abs(identifier-1), -2] += -player_identifier # Piece is in repective jail


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

        self.game_board = np.array([[5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2,       0,           0],
                                    [-5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2,       0,           0]])
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

        # if a spot has only one piece of the opposite color, return True
        if player_identifier != 0 and self.game_board[row][col] / player_identifier < 0:
            return self.game_board[row][col] == 1 or self.game_board[row][col] == -1 # this leads to jail
        # if the board spot is 0 or the player identifier that move is valid
        if self.game_board[row][col] / player_identifier >= 0:
            return True
        # print("4")
        return False


    def check_winner(self) -> None|str|int:

        """
        If there are any no pieces on the board of one color they win (including no pieces in prison)
        """
        if self.last_move is None:
            return None

        for row in range(self.rows):
            if abs(self.game_board[row][-1]) == constants.NUM_TOKENS_PER_PLAYER:
                return self.game_board[row][-1] // abs(self.game_board[row][-1])

        return None

    def can_score(self, identifier) -> bool:
        for row in range(self.rows):
            for col in range(self.cols):

                # Player 1 is in jail, return false
                if identifier > 0 and self.game_board[1][-2] > 0:
                    return False
                # Player 2 is in jail, return false
                elif identifier < 0 and self.game_board[0][-2] < 0:
                    return False

                # player 1, overlook row 1 col 6-12, and the identifier is the same sign as the one we are looking for
                if identifier > 0 and row == 0 and self.game_board[row][col] > 0:
                    return False
                elif identifier > 0 and row == 1 and col < 6 and self.game_board[row][col] > 0:
                    return False
                
                # player 2, overlook row 2 col 6-12, and the identifier is the same sign as the one we are looking for
                if identifier < 0 and row == 1 and self.game_board[row][col] < 0:
                    return False
                elif identifier < 0 and row == 0 and col < 6 and self.game_board[row][col] < 0:
                    return False
        return True



    def get_game_board_in_board(self) -> np.ndarray:
        """
        Returns game board
        """
        return self.game_board

    def get_scores(self) -> tuple[int, int]:
        """
        Returns player scores in tuple (player1_score, player2_score)
        """
        return (self.game_board[1, -1], self.game_board[0, -1])

    def get_possible_moves(self, dice_rolls,og_identifier) -> list[tuple[int, int]]|None:

        """
        Returns a list of all possible moves with current dice_rolls
        Could have repeat tiles in the same list because they have different starting tiles
        and rolls that make it be a repeated move spot
        """
        if dice_rolls is None:
            return None
        possible_moves = []
        # print(self.game_board)

        identifier = int((og_identifier + 1) / 2)

        # If piece is in jail, must move out of jail first
        if self.game_board[identifier][-2] != 0: 
            # print(self.game_board)
            # print("AI is in jail: ", self.game_board[identifier][-2])
            for i, roll in enumerate(dice_rolls):
            # if 0, or not identifier skip!
                if not dice_rolls[i][-1]:
                    continue
                move = None

                # Piece has to move somewhere on row 0 or 1 for player 1 and player 2 respectively
                # abs(identifier - 1) = 0 for player 1, 1 for player 2
                move = (abs(identifier - 1), constants.NUM_COLS - dice_rolls[i][0], i) 

                if not self.is_move_valid(move, og_identifier):
                    move = None

                if move is not None and self.is_move_valid(move, og_identifier):
                        possible_moves.append(move)
            
            # print("Possible moves in jail: ", possible_moves)
            
            return possible_moves


        for row in range(self.rows):
            for col in range(self.cols):
                if (self.game_board[row][col] == 0
                        or self.game_board[row][col] == self.game_board[row][col] // abs(self.game_board[row][col]) != og_identifier):
                    continue
                for i, roll in enumerate(dice_rolls):
                    # if 0, or not identifier skip!
                    if not dice_rolls[i][-1]:
                        continue
                    move = None

                    # First dice is always used because this for loop ascends

                    # identifier = int((og_identifier + 1) / 2) # 1 for player 1, 0 for player 2

                    # # If piece is in jail, must move out of jail first
                    # if self.game_board[identifier][-2] != 0: 

                    #     # Piece has to move somewhere on row 0 or 1 for player 1 and player 2 respectively
                    #     # abs(identifier - 1) = 0 for player 1, 1 for player 2
                    #     move = (abs(identifier - 1), constants.NUM_COLS - dice_rolls[i][0], i) 

                    #     if not self.is_move_valid(move, og_identifier):
                    #         move = None


                    if og_identifier > 0 and self.game_board[row][col] > 0:
                        if row == 0 and col - dice_rolls[i][0] < 0:
                            move = (1, abs(col - dice_rolls[i][0]) - 1, i)
                        elif row == 0:
                            move = (0, col - dice_rolls[i][0], i)
                        else:
                            move = (1, col + dice_rolls[i][0], i)
                    elif og_identifier < 0 and self.game_board[row][col] < 0:
                        if row == 1 and col - dice_rolls[i][0] < 0:
                            move = (0, abs(col - dice_rolls[i][0]) - 1, i)
                        elif row == 1:
                            move = (1, col - dice_rolls[i][0], i)
                        else:
                            move = (0, col + dice_rolls[i][0], i)

                    if move is not None and self.is_move_valid(move, og_identifier):
                        possible_moves.append(move)
        
        return possible_moves
