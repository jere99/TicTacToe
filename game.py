import copy

class CellState:
    """Defines constants for the possible states of each cell."""
    EMPTY = ' '
    PLAYER1 = 'X'
    PLAYER2 = 'O'

class Grid:
    """Represents a tic-tac-toe grid of arbitrary length and dimensionality."""

    def __init__(self, length, dimensionality):
        self.length = length
        self.dimensionality = dimensionality
        self.data = reduce(lambda data, x: [copy.copy(data) for i in range(length)], range(dimensionality), CellState.EMPTY)

    def __str__(self):
        return str(self.data)

    def get(self, *coordinates):
        if len(coordinates) != self.dimensionality: raise ValueError("${dimensionality} coordinates must be specified." % dimensionality)
        return reduce(lambda data, coordinate: data[coordinate], coordinates, self.data)

    def set(self, value, *coordinates):
        if len(coordinates) != self.dimensionality: raise ValueError("${dimensionality} coordinates must be specified." % dimensionality)
        reduce(lambda data, coordinate: data[coordinate], coordinates[:-1], self.data)[coordinates[-1]] = value
