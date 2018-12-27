import copy
import itertools

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

    def __deepcopy__(self):
        new = Grid(self.length, self.dimensionality)
        for coordinates in itertools.combinations_with_replacement(range(self.length), self.dimensionality):
            new[coordinates] = self[coordinates]
