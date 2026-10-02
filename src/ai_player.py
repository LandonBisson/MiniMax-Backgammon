import copy
import random

import numpy as np

from player_base import Player
from board import Board
from src import constants
from src.game_manager import possible_moves

"""
ai_player.py

AIPlayer chooses moves automatically.

This class does not apply moves directly to the board.
Instead, it returns the selected move, and the GameManager applies that move.

This AI player can operate in two modes:

1. Random mode:
   - Chooses a random valid move.

2. Minimax mode:
   - Evaluates possible future game states using the minimax algorithm.

"""


class AIPlayer(Player):
    def __init__(self, is_player_one, choose_random_move):
        super().__init__(is_player_one)
        self.is_ai_player = True
        self.choose_random_move = choose_random_move
        self.max_move_look_ahead = 3

        self.testing_diagnostics = {
            "wins": 0,
            "losses": 0,
            "ties": 0,
        }

    def choose_move(self, board, dice_roll) -> tuple[int, int] | None:
        possible_moves = board.get_possible_moves(dice_roll,self.identifier)
        if self.choose_random_move and possible_moves is not None:
            return random.choice(possible_moves)
        return self.find_best_move(board,dice_roll)

    def find_best_move(self, board, dice_rolls) -> tuple[int, int] | None:
        # this method will act as a maximizer for top level in minimax tree
        possible_moves = board.get_possible_moves(dice_rolls,self.identifier)
        #no possible moves
        if possible_moves == None:
            return
        opponent_identifier = self.get_other_player_identifier()

        max_score = float("-inf")
        best_move = None
        for row, col, dice_index_used in possible_moves:
            board_copy = copy.deepcopy(board)
            move = (row, col)
            # puts the move on the board
            board_copy.apply_move(move, self.identifier)
            # removes the piece from the board
            remove_move = self.get_the_remove_the_select_move(dice_rolls,dice_index_used, move,self.identifier)
            board_copy.game_board[remove_move[0]][remove_move[1]] -= self.identifier
            # move through game tree using mini max
            score = self.minimax(board_copy, False, opponent_identifier, dice_rolls,0, float("-inf"), float("inf"))

            if score > max_score:
                max_score = score
                best_move = (move[0],move[1],dice_index_used)

        return best_move

    def evaluate(self, board, opponent_identifier, depth: int) -> float | None:
        # if depth >= 1:
        #     # this randomly selects the average dice roll
        #     # (10% of the time doing 9 to account for 8.14 average roll w/ doubles)
        #     dice_roll = random.choices([8, 9], weights=[90, 10], k=1)[0]
        score = 0
        # base evaluate for win, this should be heavily weighted because wins take a while to get to
        winner_identifier = board.check_winner()
        if winner_identifier == self.identifier:
            return 20 - depth
        elif winner_identifier == opponent_identifier:
            return -20 + depth
        #TODO: TEST THIS CODE
        one_dimension_board = self.get_one_dimension_board(copy.deepcopy(board))
        # its actually not bad for pieces to be single right now (make it negative for reward)
        SINGLE_PIECE_PUNISHMENT = -5
        JAIL_PUNISHMENT = 10
        SCORE_CHANGE_PER_PIECE = 1 / 20
        black_score = 0
        white_score = (constants.NUM_COLS * constants.NUM_ROWS) * SCORE_CHANGE_PER_PIECE
        #one demensional board starts from white score zone and goes to black score zone
        for tile in one_dimension_board:
            #these multiple by tile, so more pieces on a tile square get effected more
            #PLAYER 1 AKA WHITE AKA MAX
            if tile > 0:
                #single piece on a tile is not good and is risky
                if tile == 1:
                    score -= SINGLE_PIECE_PUNISHMENT
                score += white_score * tile
            #PLAYER 2 AKA BLACK AKA MIN
            elif tile < 0:
                if tile == -1:
                    score += SINGLE_PIECE_PUNISHMENT
                score += black_score * tile
            # since black is negative this is increasing for the minimizer
            black_score -= SCORE_CHANGE_PER_PIECE
            # this is decreasing because we start out at the spot that has the max points for the maximizer
            white_score -= SCORE_CHANGE_PER_PIECE
        # if self.is_player_one and self.in_jail:
        #     score -= JAIL_PUNISHMENT
        # elif not self.is_player_one and self.in_jail:
        #     score += JAIL_PUNISHMENT

        # depth limit is hit, retyurn score
        if depth >= self.max_move_look_ahead:
            return score

        return None
    def get_one_dimension_board(self, board):
        right_side = board.game_board[0]
        left_side = np.flip(board.game_board[1])
        return left_side + right_side

    def minimax(self, board, is_maximizing, opponent_identifier,dice_roll, depth: int = 0, alpha=float("-inf"),
                beta=float("inf")) -> float:
        # print(depth)
        score = self.evaluate(board, opponent_identifier, depth)
        if score is not None:
            return score
        # this is for a random average (kind of wrong but the average is right and should work itself out)
        if depth > 1:
            roll_one = random.randint(1, 7)
            roll_two = 7 - roll_one
            dice_roll = [[roll_one,True], [roll_two,True]]
        if is_maximizing:
            max_score = float("-inf")
            possible_moves = board.get_possible_moves(dice_roll,self.identifier)
            # print("Possible", possible_moves)
            for row, col, roll_index in possible_moves:
                board_copy = copy.deepcopy(board)
                move = (row, col)
                board_copy.apply_move(move, self.identifier)
                remove_move = self.get_the_remove_the_select_move(dice_roll, roll_index, move,self.identifier)
                board_copy.game_board[remove_move[0]][remove_move[1]] -= self.identifier

                score = self.minimax(board_copy, not is_maximizing, opponent_identifier, dice_roll, depth + 1)

                max_score = max(score, max_score)
                alpha = max(alpha, score)
                if alpha >= beta:
                    print("Pruning")
                    break

            return max_score

        else:
            min_score = float("inf")
            possible_moves = board.get_possible_moves(dice_roll,opponent_identifier)
            # print("Possible", possible_moves)
            for row, col, roll_index in possible_moves:
                board_copy = copy.deepcopy(board)
                move = (row, col)
                board_copy.apply_move(move, opponent_identifier)
                remove_move = self.get_the_remove_the_select_move(dice_roll, roll_index, move,opponent_identifier)
                board_copy.game_board[remove_move[0]][remove_move[1]] -= opponent_identifier

                score = self.minimax(board_copy, not is_maximizing, opponent_identifier,dice_roll, depth + 1, alpha, beta)

                min_score = min(score, min_score)
                beta = min(beta, score)
                if alpha >= beta:
                    print("Pruning")
                    break

            return min_score
    def get_the_remove_the_select_move(self, dice_rolls, dice_index_used, move, og_identifier):
        # return None
        roll = dice_rolls[dice_index_used][0]
        row, col = move
        identifier = int((og_identifier + 1) / 2)  # 0 for black, 1 for white
        other_row = abs(identifier - 1)
        # if row is 1 and black  or row is 1 and white (we need right movement for each of these cases)
        if (row == 0 and og_identifier == constants.PLAYER_1_IDENTIFIER) or (row == 1 and og_identifier == constants.PLAYER_2_IDENTIFIER):
            src_col = col + roll
            # jumping over board
            if src_col < 0:
                print("JUMP remove 1")
                return identifier, abs(src_col) - 1
            # moving towards jumping WORKING
            print("MOVE TOWARDS JUMP remove 2")
            return other_row, src_col
        #passed the jumping portion but the roll might be
        src_col = col - roll
        if src_col < 0:
            print("PASSED JUMP remove last row remove 3")
            return other_row, abs(src_col) - 1
        print("PASSED JUMP remove 4")
        return identifier, src_col



    def update_testing_diagnostics(self, last_game_result):

        if last_game_result in self.testing_diagnostics:
            self.testing_diagnostics[last_game_result] += 1

        player = "player 1" if self.is_player_one else "player 2"
        ai_mode = "choose random move" if self.choose_random_move else "minimax"
        print("-------------------------------------------------")
        print(f"Testing diagnostics for {player}:")
        print(f"AI mode: {ai_mode}")
        print(
            f"wins: {self.testing_diagnostics["wins"]}, losses: {self.testing_diagnostics["losses"]}, ties: {self.testing_diagnostics["ties"]}")

