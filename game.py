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

    memoizedLines = {}

    @classmethod
    def generateLines(cls, length, dimensionality):
        if (length, dimensionality) not in cls.memoizedLines:
            directions = list(itertools.chain(*[list(itertools.combinations(range(dimensionality), d)) for d in range(1, dimensionality + 1)]))
            lines = []
            for d in range(dimensionality):
                for dir in filter(lambda direction: d in direction, directions):
                    lines += map(lambda cell: tuple(sorted([tuple([cell[i] + x if cell[i] == 0 and i in dir else cell[i] - x if cell[i] == length - 1 and i in dir else cell[i] for i in range(dimensionality)]) for x in range(length)])), filter(lambda cell: reduce(lambda acc, dimension: acc and (cell[dimension] == 0 or cell[dimension] == length - 1), dir, True), itertools.product(range(length), repeat=dimensionality)))
            cls.memoizedLines[(length, dimensionality)] = set(lines)
        return cls.memoizedLines[(length, dimensionality)]

    def __init__(self, length, dimensionality):
        self.length = length
        self.dimensionality = dimensionality
        self.lines = self.generateLines(length, dimensionality)
        self.data = reduce(lambda data, x: [copy.deepcopy(data) for i in range(length)], range(dimensionality), CellState.EMPTY)

    def __eq__(self, other):
        return type(other) is Grid and self.data == other.data

    def __nonzero__(self):
        return reduce(lambda result, cell: result or cell != CellState.EMPTY, self, False)

    def __str__(self):
        return str(self.data)

    def __getitem__(self, coordinates):
        if type(coordinates) is int: coordinates = (coordinates,)
        if len(coordinates) != self.dimensionality: raise ValueError("Expected %d coordinates." % self.dimensionality)
        return reduce(lambda data, coordinate: data[coordinate], coordinates, self.data)

    def __setitem__(self, coordinates, value):
        if type(coordinates) is int: coordinates = (coordinates,)
        if len(coordinates) != self.dimensionality: raise ValueError("Expected %d coordinates." % self.dimensionality)
        reduce(lambda data, coordinate: data[coordinate], coordinates[:-1], self.data)[coordinates[-1]] = value

    def coordinatesIterator(self):
        return itertools.product(range(self.length), repeat=self.dimensionality)

    def __iter__(self):
        return iter(map(lambda coordinates: self[coordinates], self.coordinatesIterator()))

    def __copy__(self):
        new = Grid(self.length, self.dimensionality)
        new.data = self.data
        return new

    def __deepcopy__(self, memodict={}):
        new = Grid(self.length, self.dimensionality)
        for coordinates in self.coordinatesIterator():
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
        return [] if self.isWin(CellState.PLAYER1) or self.isWin(CellState.PLAYER2) else filter(lambda coordinates: self.board[coordinates] == CellState.EMPTY, self.board.coordinatesIterator())

    def isWin(self, player):
        return player and reduce(lambda found, line: found or reduce(lambda success, cell: success and self.board[cell] == player, line, True), self.board.lines, False)

    def getWinningLine(self, player):
        return player and reduce(lambda found, line: found if found else line if reduce(lambda success, cell: success and self.board[cell] == player, line, True) else None, self.board.lines, None)

    def getFilledCells(self):
        return map(lambda coordinates: (coordinates, self.board[coordinates]), filter(lambda coordinates: self.board[coordinates] != CellState.EMPTY, self.board.coordinatesIterator()))

class Game:
    """Represents a game of tic-tac-toe."""

    def __init__(self, length, dimensionality):
        self.length = length
        self.dimensionality = dimensionality
        self.state = GameState(Grid(length, dimensionality), CellState.PLAYER1)

    def __str__(self):
        return "A %s game of Tic-Tac-Toe | %s, Winner: %s" % ('x'.join(itertools.repeat(str(self.length), self.dimensionality)), str(self.state), self.getWinner())

    def __copy__(self):
        new = Game(self.length, self.dimensionality)
        new.state = self.state
        return new

    def __deepcopy__(self, memodict={}):
        new = Game(self.length, self.dimensionality)
        new.state = copy.deepcopy(self.state)
        return new

    def makeMove(self, coordinates):
        if coordinates not in self.state.getLegalActions(): return False
        self.state = self.state.generateSuccessor(coordinates)
        return True

    def getWinner(self):
        player1, player2 = self.state.isWin(CellState.PLAYER1), self.state.isWin(CellState.PLAYER2)
        if player1 and player2: raise Exception("Game state is invalid -- both players have won.")
        winner = CellState.PLAYER1 if player1 else CellState.PLAYER2 if player2 else None
        return (winner, self.state.getWinningLine(winner))

    def getFilledCells(self):
        return self.state.getFilledCells()
