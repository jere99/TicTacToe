from copy import copy
import functools
import itertools


def matrix_to_bitmask(grid):
    """
    Converts a 3x3 bit-matrix to a bitmask.

    Parameters:
        grid (tuple) 3x3 bit-matrix
    Raises:
        TypeError if the grid is not a tuple or has the wrong dimensions
        ValueError if any of the entries of the matrix are not bit-valued
    Returns:
        (int) bitmask representation of the matrix
    """
    if not isinstance(grid, tuple) or len(grid) != 3:
        raise TypeError("Grid is not valid.")
    for row in grid:
        if not isinstance(row, tuple) or len(row) != 3:
            raise TypeError("Grid is not valid.")
    for cell in itertools.chain.from_iterable(grid):
        if int(cell) not in {0, 1}:
            raise ValueError(f"{cell} is not a valid bit value.")

    return functools.reduce(lambda acc, cell: acc << 1 | cell, itertools.chain.from_iterable(grid))


def bit_sum(bitmask):
    """
    Calculates the number of 1s in the binary representation of a number.

    Parameters:
        bitmask (int) the number to process
    Returns:
        (int) the number of 1s in the binary representation
    """
    count = 0
    while bitmask:
        count += bitmask & 1
        bitmask >>= 1
    return count


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
            player1 (tuple|int) 3x3 bit-matrix or bitmask representing the first player's cells
            player2 (tuple|int) 3x3 bit-matrix or bitmask representing the second player's cells
            turn (bool) True if it's the first player's turn, False if it's the second player's turn
        Raises:
            TypeError if either matrix is neither an int nor a tuple or has the wrong dimensions
            RuntimeError if the specified position is not valid
        """
        self.player1 = player1 if isinstance(player1, int) else matrix_to_bitmask(player1)
        self.player2 = player2 if isinstance(player2, int) else matrix_to_bitmask(player2)
        self.turn = bool(turn)
        self.validate()

    def __eq__(self, other):
        """
        Parameters:
            other (GameState) the object to compare to
        Returns:
            (bool) True if the two GameStates have the same bitmasks for both players, False otherwise
        """
        return isinstance(other, GameState) and not (self.player1 ^ other.player1 | self.player2 ^ other.player2)

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the GameState
        """
        return "\n--+---+--\n".join(map(lambda row: " | ".join(map(lambda column: self[(row, column)], range(3))), range(3)))

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
        The characters are specified in the class constants PLAYER_1 and PLAYER_2.

        Parameters:
            cell (tuple) the coordinates of the cell to access
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            KeyError if the specified indices are not within the valid range
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
                raise KeyError(f"{coordinate} is out of range.")

        bitmask = 1 << (8 - (cell[0] * 3 + cell[1]))
        return self.PLAYER_1 if self.player1 & bitmask else self.PLAYER_2 if self.player2 & bitmask else self.EMPTY_CELL

    def __copy__(self):
        """
        Returns:
            (GameState) a new object with with the bitmask for each player copied from the existing GameState
        """
        return GameState(self.player1, self.player2, self.turn)

    def gridFilled(self):
        """
        Determines whether the grid is completely filled and no further moves are possible.

        Returns:
            (bool) True if the grid is filled, False otherwise
        """
        return not (0x1FF ^ (self.player1 | self.player2))

    def isWin(self, turn):
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
        Determines whether the GameState represents a valid TicTacToe position.
        A valid TicTacToe position satisfies the following conditions:
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
        if self.isWin(True) and self.isWin(False):
            raise RuntimeError("Both players have won.")
        if self.isWin(self.turn):
            raise RuntimeError("Player with current turn has won.")

    def emptyCells(self):
        """
        Generates a list of the coordinates of all unoccupied cells.

        Returns:
            (list) tuples of the coordinates of all unoccupied cells
        """
        result = []
        bitmask = self.player1 | self.player2
        for i in range(9):
            if not (bitmask & 1):
                result.append(((8 - i) // 3, (8 - i) % 3))
            bitmask >>= 1
        return result

    def generateSuccessor(self, cell):
        """
        Generates a GameState which represents the position after one move is made from the current GameState.

        Parameters:
            cell (tuple) the coordinates of the cell to be updated
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            KeyError if the specified indices are not within the valid range
            ValueError if the cell is already occupied
        Returns:
            (GameState) the successor position
        """
        if cell not in self.emptyCells():
            raise ValueError(f"{cell} is already occupied.")
        bitmask = 1 << (8 - (cell[0] * 3 + cell[1]))
        return GameState(self.player1 | bitmask if self.turn else self.player1, self.player2 if self.turn else self.player2 | bitmask, not self.turn)


if __name__ == '__main__':
    print(bin(matrix_to_bitmask(GameState.EMPTY_GRID)))
    print(bin(matrix_to_bitmask(((1, 0, 0), (0, 1, 0), (0, 0, 1)))))
    try:
        print(bin(matrix_to_bitmask(((0, 0, 0), (1, 1, 1), (2, 2, 2)))))  # ValueError
    except ValueError as error:
        print(error)

    g = GameState()
    print(g)
    for cell in [(0, 0), (1, 0), (1, 1), (2, 2), (0, 1), (0, 2), (2, 1)]:
        print(g.emptyCells())
        g = g.generateSuccessor(cell)
        print(g)

# import copy
# import itertools
#
# class CellState:
#     """Defines constants for the possible states of each cell."""
#     EMPTY = ' '
#     PLAYER1 = 'X'
#     PLAYER2 = 'O'
#
#     NEXT = {PLAYER1: PLAYER2, PLAYER2: PLAYER1}
#
# class Grid:
#     """Represents an n-dimensional tic-tac-toe grid of arbitrary size."""
#
#     memoizedLines = {}
#
#     @classmethod
#     def generateLines(cls, length, dimensionality):
#         if (length, dimensionality) not in cls.memoizedLines:
#             directions = list(itertools.chain(*[list(itertools.combinations(range(dimensionality), d)) for d in range(1, dimensionality + 1)]))
#             lines = []
#             for d in range(dimensionality):
#                 for dir in filter(lambda direction: d in direction, directions):
#                     lines += map(lambda cell: tuple(sorted([tuple([cell[i] + x if cell[i] == 0 and i in dir else cell[i] - x if cell[i] == length - 1 and i in dir else cell[i] for i in range(dimensionality)]) for x in range(length)])), filter(lambda cell: reduce(lambda acc, dimension: acc and (cell[dimension] == 0 or cell[dimension] == length - 1), dir, True), itertools.product(range(length), repeat=dimensionality)))
#             cls.memoizedLines[(length, dimensionality)] = set(lines)
#         return cls.memoizedLines[(length, dimensionality)]
#
#     def __init__(self, length, dimensionality):
#         self.length = length
#         self.dimensionality = dimensionality
#         self.lines = self.generateLines(length, dimensionality)
#         self.data = reduce(lambda data, x: [copy.deepcopy(data) for i in range(length)], range(dimensionality), CellState.EMPTY)
#
#     def __eq__(self, other):
#         return type(other) is Grid and self.data == other.data
#
#     def __nonzero__(self):
#         return reduce(lambda result, cell: result or cell != CellState.EMPTY, self, False)
#
#     def __str__(self):
#         return str(self.data)
#
#     def __getitem__(self, coordinates):
#         if type(coordinates) is int: coordinates = (coordinates,)
#         if len(coordinates) != self.dimensionality: raise ValueError("Expected %d coordinates." % self.dimensionality)
#         return reduce(lambda data, coordinate: data[coordinate], coordinates, self.data)
#
#     def __setitem__(self, coordinates, value):
#         if type(coordinates) is int: coordinates = (coordinates,)
#         if len(coordinates) != self.dimensionality: raise ValueError("Expected %d coordinates." % self.dimensionality)
#         reduce(lambda data, coordinate: data[coordinate], coordinates[:-1], self.data)[coordinates[-1]] = value
#
#     def coordinatesIterator(self):
#         return itertools.product(range(self.length), repeat=self.dimensionality)
#
#     def __iter__(self):
#         return iter(map(lambda coordinates: self[coordinates], self.coordinatesIterator()))
#
#     def __copy__(self):
#         new = Grid(self.length, self.dimensionality)
#         new.data = self.data
#         return new
#
#     def __deepcopy__(self, memodict={}):
#         new = Grid(self.length, self.dimensionality)
#         for coordinates in self.coordinatesIterator():
#             new[coordinates] = self[coordinates]
#         return new
#
# class GameState:
#     """Represents a state of a game of tic-tac-toe."""
#
#     def __init__(self, board, turn):
#         self.board = board
#         self.turn = turn
#
#     def __eq__(self, other):
#         return type(other) is GameState and self.board == other.board and self.turn == other.turn
#
#     def __str__(self):
#         return "Turn: %s, Board: %s" % (self.turn, str(self.board))
#
#     def __copy__(self):
#         return GameState(self.board, self.turn)
#
#     def __deepcopy__(self, memodict={}):
#         return GameState(copy.deepcopy(self.board), self.turn)
#
#     def generateSuccessor(self, coordinates):
#         successor = copy.deepcopy(self)
#         successor.board[coordinates] = successor.turn
#         successor.turn = CellState.NEXT[successor.turn]
#         return successor
#
#     def getLegalActions(self):
#         return [] if self.isWin(CellState.PLAYER1) or self.isWin(CellState.PLAYER2) else filter(lambda coordinates: self.board[coordinates] == CellState.EMPTY, self.board.coordinatesIterator())
#
#     def isWin(self, player):
#         return player and reduce(lambda found, line: found or reduce(lambda success, cell: success and self.board[cell] == player, line, True), self.board.lines, False)
#
#     def getWinningLine(self, player):
#         return player and reduce(lambda found, line: found if found else line if reduce(lambda success, cell: success and self.board[cell] == player, line, True) else None, self.board.lines, None)
#
#     def getFilledCells(self):
#         return map(lambda coordinates: (coordinates, self.board[coordinates]), filter(lambda coordinates: self.board[coordinates] != CellState.EMPTY, self.board.coordinatesIterator()))
#
# class Game:
#     """Represents a game of tic-tac-toe."""
#
#     def __init__(self, length, dimensionality):
#         self.length = length
#         self.dimensionality = dimensionality
#         self.state = GameState(Grid(length, dimensionality), CellState.PLAYER1)
#
#     def __str__(self):
#         return "A %s game of Tic-Tac-Toe | %s, Winner: %s" % ('x'.join(itertools.repeat(str(self.length), self.dimensionality)), str(self.state), self.getWinner())
#
#     def __copy__(self):
#         new = Game(self.length, self.dimensionality)
#         new.state = self.state
#         return new
#
#     def __deepcopy__(self, memodict={}):
#         new = Game(self.length, self.dimensionality)
#         new.state = copy.deepcopy(self.state)
#         return new
#
#     def makeMove(self, coordinates):
#         if coordinates not in self.state.getLegalActions(): return False
#         self.state = self.state.generateSuccessor(coordinates)
#         return True
#
#     def getWinner(self):
#         player1, player2 = self.state.isWin(CellState.PLAYER1), self.state.isWin(CellState.PLAYER2)
#         if player1 and player2: raise Exception("Game state is invalid -- both players have won.")
#         winner = CellState.PLAYER1 if player1 else CellState.PLAYER2 if player2 else None
#         return (winner, self.state.getWinningLine(winner))
#
#     def getFilledCells(self):
#         return self.state.getFilledCells()
