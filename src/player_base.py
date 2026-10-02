
"""
player_base.py

Base class for AI and human players.
"""
from src import constants


class Player:
    def __init__(self, is_player_one: bool):

        self.is_player_one = is_player_one

        # These identifiers are used by Board to store moves in a numpy grid.
        self.identifier = None
        if is_player_one:
            self.identifier = constants.PLAYER_1_IDENTIFIER
        else:
            self.identifier = constants.PLAYER_2_IDENTIFIER

        # Intended to be set by derived classes (HumanPlayer / AIPlayer)
        self.is_ai_player = None

        self.can_score = False

        self.score = 0
        self.in_jail = False


    def get_other_player_identifier(self):

        if self.is_player_one:
            return constants.PLAYER_2_IDENTIFIER
        else:
            return constants.PLAYER_1_IDENTIFIER


    def choose_move(self, board, move_input):

        """
        Choose a move to apply to the board.
        This method must be implemented by subclasses.
        """

        raise NotImplementedError("Derived classes must implement choose_move().")

