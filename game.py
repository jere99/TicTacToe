import copy
import itertools

class CellState:
    """Defines constants for the possible states of each cell."""
    EMPTY = ' '
    PLAYER1 = 'X'
    PLAYER2 = 'O'

    NEXT = {PLAYER1: PLAYER2, PLAYER2: PLAYER1}

class Grid:
    """Represents an n-dimensional tic-tac-toe grid of arbitrary size."""

    def __init__(self, length, dimensionality):
        self.length = length
        self.dimensionality = dimensionality
        self.data = reduce(lambda data, x: [copy.deepcopy(data) for i in range(length)], range(dimensionality), CellState.EMPTY)

    def __getitem__(self, coordinates):
        if type(coordinates) is int: coordinates = (coordinates,)
        if len(coordinates) != self.dimensionality: raise ValueError("Expected %d coordinates." % self.dimensionality)
        return reduce(lambda data, coordinate: data[coordinate], coordinates, self.data)

    def __setitem__(self, coordinates, value):
        if type(coordinates) is int: coordinates = (coordinates,)
        if len(coordinates) != self.dimensionality: raise ValueError("Expected %d coordinates." % self.dimensionality)
        reduce(lambda data, coordinate: data[coordinate], coordinates[:-1], self.data)[coordinates[-1]] = value

    def __eq__(self, other):
        return type(other) is Grid and self.data == other.data

    def __str__(self):
        return str(self.data)

    def __copy__(self):
        new = Grid(self.length, self.dimensionality)
        new.data = self.data
        return new

    def __deepcopy__(self, memodict={}):
        new = Grid(self.length, self.dimensionality)
        for coordinates in itertools.product(range(self.length), repeat=self.dimensionality):
            new[coordinates] = self[coordinates]
        return new

class GameState:
    """Represents a state of a game of tic-tac-toe."""

    def __init__(self, board, turn):
        self.board = board
        self.turn = turn

    def __eq__(self, other):
        return type(other) is GameState and self.board == other.board and self.turn == other.turn

    def __str__(self):
        return "Turn: %s, Board: %s" % (self.turn, str(self.board))

    def __copy__(self):
        return GameState(self.board, self.turn)

    def __deepcopy__(self, memodict={}):
        return GameState(copy.deepcopy(self.board), self.turn)

    def generateSuccessor(self, coordinates):
        successor = copy.deepcopy(self)
        successor.board[coordinates] = successor.turn
        successor.turn = CellState.NEXT[successor.turn]
        return successor

    def getLegalActions(self):
        return [] if self.isWin(CellState.PLAYER1) or self.isWin(CellState.PLAYER2) else filter(lambda coordinates: self.board[coordinates] == CellState.EMPTY, itertools.product(range(self.board.length), repeat=self.board.dimensionality))

    def isWin(self, player):
        return False
