import functools
import itertools


def matrix_to_bitstring(grid):
    """
    Converts a 3x3 bit-matrix to a bitstring.
    The bitstring representation is row-major with the (0,0) cell being represented in the 9th bit from the right.

    Parameters:
        grid (tuple) 3x3 bit-matrix
    Raises:
        TypeError if the grid is not a tuple or has the wrong dimensions
        ValueError if any of the entries of the matrix are not bit-valued
    Returns:
        (int) bitstring representation of the matrix
    """
    if not isinstance(grid, tuple) or len(grid) != 3:
        raise TypeError("Grid is not valid.")
    for row in grid:
        if not isinstance(row, tuple) or len(row) != 3:
            raise TypeError("Grid is not valid.")
    for cell in itertools.chain.from_iterable(grid):
        if int(cell) not in {0, 1}:
            raise ValueError(cell + " is not a valid bit value.")

    return functools.reduce(lambda acc, cell: acc << 1 | cell, itertools.chain.from_iterable(grid))


def bit_sum(bitstring):
    """
    Calculates the number of 1s in the binary representation of a number.

    Parameters:
        bitstring (int) the number to process
    Returns:
        (int) the number of 1s in the binary representation
    """
    count = 0
    while bitstring:
        count += bitstring & 1
        bitstring >>= 1
    return count


def occupied_cells(bitstring):
    """
    Generates a list of coordinates of the cells which are occupied in a bitstring representation of a 3x3 bit-matrix.
    Assumes that the bits are in row-major order and the (0,0) cell is represented by the 9th bit from the right.

    Parameters:
        bitstring (int) a bitstring representing a 3x3 bit-matrix
    Returns:
        (list) tuples of cooordinates which have a value of 1 in the bitstring
    """
    result = []
    for i in range(9):
        if bitstring & 1:
            result.append(((8 - i) // 3, (8 - i) % 3))
        bitstring >>= 1
    return result


class GameState:
    """Immutable object which represents the state of a Tic-Tac-Toe game."""

    EMPTY_CELL = ' '
    PLAYER_1 = 'X'
    PLAYER_2 = 'O'
    EMPTY_GRID = ((0, 0, 0), (0, 0, 0), (0, 0, 0))

    WINNING_SEQUENCES = [
        0b111000000,
        0b000111000,
        0b000000111,
        0b100100100,
        0b010010010,
        0b001001001,
        0b100010001,
        0b001010100
    ]

    def __init__(self, player1=EMPTY_GRID, player2=EMPTY_GRID, turn=True):
        """
        Creates a game state from two 3x3 bit-matrices.

        Parameters:
            player1 (tuple|int) 3x3 bit-matrix or bitstring representing the first player's cells
            player2 (tuple|int) 3x3 bit-matrix or bitstring representing the second player's cells
            turn (bool) True if it's the first player's turn, False if it's the second player's turn
        Raises:
            TypeError if either matrix is neither an int nor a tuple or has the wrong dimensions
            RuntimeError if the specified position is not valid
        """
        self.player1 = player1 if isinstance(player1, int) else matrix_to_bitstring(player1)
        self.player2 = player2 if isinstance(player2, int) else matrix_to_bitstring(player2)
        self.turn = bool(turn)
        self.validate()

    def __eq__(self, other):
        """
        Parameters:
            other (GameState) the object to compare to
        Returns:
            (bool) True if the two GameStates have the same bitstrings for both players, False otherwise
        """
        return isinstance(other, GameState) and not (self.player1 ^ other.player1 | self.player2 ^ other.player2)

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the GameState
        """
        return "\n\t--+---+--\n".join(map(lambda row: "\t" + " | ".join(map(lambda column: self[(row, column)], range(3))), range(3)))

    def __hash__(self):
        """
        Returns:
            (int) a hash of the GameState
        """
        return self.player1 << 9 | self.player2

    def __bool__(self):
        """
        Returns:
            (bool) True if the GameState represents an empty board, False otherwise
        """
        return bool(self.player1 | self.player2)

    def __getitem__(self, cell):
        """
        Returns a single-character representation of one of the cells in the GameState.
        The characters are specified in the class constants PLAYER_1, PLAYER_2, and EMPTY_CELL.

        Parameters:
            cell (tuple) the coordinates of the cell to access
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            IndexError if the specified indices are not within the valid range
        Returns:
            (str) the single-character representation for the specified cell
        """
        if not isinstance(cell, tuple):
            raise TypeError("Cell must be a tuple.")
        if len(cell) != 2:
            raise TypeError("Exactly two coordinates must be specified.")
        for coordinate in cell:
            if not isinstance(coordinate, int):
                raise TypeError("Each coordinate must be an integer.")
            if coordinate not in range(3):
                raise IndexError(coordinate + " is out of range.")

        bitmask = 1 << (8 - (cell[0] * 3 + cell[1]))
        return self.PLAYER_1 if self.player1 & bitmask else self.PLAYER_2 if self.player2 & bitmask else self.EMPTY_CELL

    def __copy__(self):
        """
        Returns:
            (GameState) a new object with with the bitstring for each player copied from the existing GameState
        """
        return GameState(self.player1, self.player2, self.turn)

    def get_turn(self):
        """
        Returns:
            (bool) True if it is the first player's turn, False if it is the second player's turn
        """
        return self.turn

    def is_grid_filled(self):
        """
        Determines whether the grid is completely filled and no further moves are possible.

        Returns:
            (bool) True if the grid is filled, False otherwise
        """
        return not (0x1FF ^ (self.player1 | self.player2))

    def is_win(self, turn):
        """
        Determines whether a particular player has a winning sequence

        Parameters:
            turn (bool) True if checking the first player, False if checking the second player
        Returns:
            (bool) True if the specified player has a winning sequence, False otherwise
        """
        playermask = self.player1 if turn else self.player2
        for sequence in self.WINNING_SEQUENCES:
            if not (playermask & sequence ^ sequence):
                return True
        return False

    def validate(self):
        """
        Determines whether the GameState represents a valid Tic-Tac-Toe position.
        A valid Tic-Tac-Toe position satisfies the following conditions:
            1) only one player occupies each cell
            2) the turn is consistent with the number of cells occupied by each player
            3) at most one player has a winning sequence
            4) if a player has a winning sequence, it is not their turn

        Raises:
            RuntimeError if any of these conditions are not satisfied
        Returns: (None)
        """
        if self.player1 & self.player2:
            raise RuntimeError("Cell is occupied by both players.")
        if bit_sum(self.player1) - bit_sum(self.player2) - int(not self.turn):
            raise RuntimeError("Cell distribution is invalid.")
        if self.is_win(True) and self.is_win(False):
            raise RuntimeError("Both players have won.")
        if self.is_win(self.turn):
            raise RuntimeError("Player with current turn has won.")

    def get_cell_states(self):
        """
        Generates a dictionary that maps the coordinates of each cell to its state.

        Returns:
            (dict) map of cell coordinates to the string representation of its state
        """
        player1 = [(c, self.PLAYER_1) for c in occupied_cells(self.player1)]
        player2 = [(c, self.PLAYER_2) for c in occupied_cells(self.player2)]
        empty = [(c, self.EMPTY_CELL) for c in self.get_empty_cells()]
        return dict(player1 + player2 + empty)

    def get_empty_cells(self):
        """
        Generates a list of the coordinates of all unoccupied cells.

        Returns:
            (list) tuples of the coordinates of all unoccupied cells
        """
        return occupied_cells((0x1FF ^ (self.player1 | self.player2)))

    def generate_successor(self, cell):
        """
        Generates a GameState which represents the position after one move is made from the current GameState.

        Parameters:
            cell (tuple) the coordinates of the cell to be updated
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            IndexError if the specified indices are not within the valid range
            ValueError if the cell is already occupied
        Returns:
            (GameState) the successor position
        """
        if cell not in self.get_empty_cells():
            raise ValueError(cell + " is already occupied.")
        bitmask = 1 << (8 - (cell[0] * 3 + cell[1]))
        return GameState(self.player1 | bitmask if self.turn else self.player1, self.player2 if self.turn else self.player2 | bitmask, not self.turn)


class Game:
    """Object which represents a Tic-Tac-Toe game."""

    def __init__(self):
        """
        Creates a new game with an empty board.
        """
        self.state = GameState()

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the Game
        """
        result = self.state.PLAYER_1 + " Wins!" if self.state.is_win(True) else self.state.PLAYER_2 + " Wins!" if self.state.is_win(False) else "Draw!"
        return "A 3x3 game of Tic-Tac-Toe\n" + str(self.state) + ("" if self else "\nResult: " + result)

    def __bool__(self):
        """
        Returns:
            (bool) True if the game is not over, False otherwise
        """
        return not self.state.is_grid_filled() and not self.state.is_win(True) and not self.state.is_win(False)

    def get_turn(self):
        """
        Returns:
            (bool) True if it is the first player's turn, False if it is the second player's turn
        """
        return self.state.get_turn()

    def get_cell(self, cell):
        """
        Returns a single-character representation of one of the cells in the GameState.
        The characters are specified in the class constants PLAYER_1, PLAYER_2, and EMPTY_CELL.

        Parameters:
            cell (tuple) the coordinates of the cell to access
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            IndexError if the specified indices are not within the valid range
        Returns:
            (str) the single-character representation for the specified cell
        """
        return self.state[cell]

    def evaluate(self):
        """
        Evaluates a Game which is completed.

        Raises:
            RuntimeError if the Game is not over
        Returns:
            (int) 1 if player 1 has won
                 -1 if player 2 has won
                  0 if the game is a draw
        """
        if self:
            raise RuntimeError("Game is not over.")
        return 1 if self.state.is_win(True) else -1 if self.state.is_win(False) else 0

    def get_cell_states(self):
        """
        Generates a dictionary that maps the coordinates of each cell to its state.

        Returns:
            (dict) map of cell coordinates to the string representation of its state
        """
        return self.state.get_cell_states()

    def get_legal_actions(self):
        """
        Generates a list of legal moves (unoccupied cells).

        Returns:
            (list) tuples of the coordinates of all unoccupied cells
        """
        return self.state.get_empty_cells()

    def make_move(self, cell):
        """
        Makes a move for the player whose turn it currently is.

        Parameters:
            cell (tuple) the coordinates of the cell to be updated
        Returns:
            (bool) True if the move is completed successfully, False otherwise
        """
        try:
            self.state = self.state.generate_successor(cell)
            return True
        except (TypeError, IndexError, ValueError, RuntimeError):
            return False


if __name__ == '__main__':
    g = Game()
    print(g)
    for cell in [(0, 0), (1, 0), (1, 1), (2, 2), (0, 1), (0, 2), (2, 1)]:
        g.make_move(cell)
        print(g)
        print(g.get_legal_actions())
        print(g.get_filled_cells())
