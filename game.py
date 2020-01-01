from copy import copy, deepcopy
from functools import reduce
from itertools import chain, combinations


def matrix_to_bitstring(grid):
    """
    Converts a nxn bit-matrix to a bitstring.
    The bitstring representation is row-major with the (0,0) cell being represented in the most leftmost bit.

    Parameters:
        grid (tuple) nxn bit-matrix
    Raises:
        TypeError if the grid is not nested tuples or is not square
        ValueError if any of the entries of the matrix are not bit-valued
    Returns:
        (int) bitstring representation of the matrix
    """
    if not isinstance(grid, tuple):
        print(grid)
        print(type(grid))
        raise TypeError("Grid is not a tuple.")
    length = len(grid)
    for row in grid:
        if not isinstance(row, tuple):
            raise TypeError("Row is not a tuple.")
        if len(row) != length:
            raise TypeError("Grid is not square.")
    for cell in chain.from_iterable(grid):
        if int(cell) not in {0, 1}:
            raise ValueError("{} is not a valid bit value.".format(cell))

    return reduce(lambda acc, cell: acc << 1 | cell, chain.from_iterable(grid), 0)


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


def occupied_cells(bitstring, n):
    """
    Generates a list of coordinates of the cells which are occupied in a bitstring representation of a nxn bit-matrix.
    Assumes that the bits are in row-major order and the (0,0) cell is represented by the leftmost bit.

    Parameters:
        bitstring (int) a bitstring representing a nxn bit-matrix
        length (int) the dimension of the matrix
    Returns:
        (list) tuples of cooordinates which have a value of 1 in the bitstring
    """
    result = []
    for i in range(n ** 2):
        if bitstring & 1:
            result.append(((n ** 2 - 1 - i) // n, (n ** 2 - 1 - i) % n))
        bitstring >>= 1
    return result


class Player(object):
    """Wrapper object that represents a player with a unique representation."""

    @property
    def representation(self):
        """
        Returns:
            (str) a single character that serves as the Player's unique identifier
        """
        return self._representation

    @representation.setter
    def representation(self, value):
        """
        Parameters:
            value (str) a single character that serves as the Player's unique identifier
        Raises:
            TypeError if the representation is invalid
        """
        try:
            ord(value)
        except TypeError:
            raise TypeError("The player representation must be a single character.")
        self._representation = value

    @property
    def next(self):
        """
        Raises:
            RuntimeError if the next Player has not been set
        Returns:
            (Player) the next Player in the turn order
        """
        if not self._next:
            raise RuntimeError("No next player has been set.")
        return self._next

    @next.setter
    def next(self, value):
        """
        Parameters:
            value (Player) the next Player in the turn order
        """
        self._next = value

    def __init__(self, representation):
        """
        Creates a Player with a unique string representation.

        Parameters:
            representation (str) a single character that does not belong to any existing player
        Raises:
            TypeError if the string representation is invalid
        """
        try:
            ord(representation)
        except TypeError:
            raise TypeError("The player representation must be a single ascii character.")
        self.representation = representation
        self.next = self

    def __eq__(self, other):
        """
        Parameters:
            other (Player) the object to compare to
        Returns:
            (bool) True if the two Players have the same representation, False otherwise
        """
        return self.representation == other.representation

    def __str__(self):
        """
        Returns:
            (str) the Player's representation
        """
        return self.representation

    def __hash__(self):
        """
        Returns:
            (int) a hash of the Player
        """
        return ord(self.representation)


class GameState(object):
    """Immutable object which represents the state of a Tic-Tac-Toe game."""

    EMPTY_CELL = ' '

    _winning_sequences = {}

    @classmethod
    def generate_winning_sequences(cls, length):
        """
        Generates the bitstrings that represent the winning sequences for a grid of arbitrary size.
        The results are cached on the class so that they only need to be generated once.

        Parameters:
            length (int) the side length of grid to generate sequence for
        """
        sequences = []
        row = (1 << length) - 1
        column = reduce(lambda acc, _: acc << length | 1, range(length), 0)
        for _ in range(length):
            sequences.extend([row, column])
            row <<= length
            column <<= 1
        sequences.append(reduce(lambda acc, i: acc | 1 << i * (length + 1), range(length), 0))
        sequences.append(reduce(lambda acc, i: acc | 1 << (i + 1) * (length - 1), range(length), 0))
        cls._winning_sequences[length] = set(sequences)  # Remove duplicates

    @property
    def winning_sequences(self):
        """
        Accesses the winning sequences for the GameState based on its length.
        Generates the sequences if they are not already cached.

        Returns:
            (set) the winning sequences for the GameState
        """
        if self.length not in self._winning_sequences:
            self.generate_winning_sequences(self.length)
        return self._winning_sequences[self.length]

    @property
    def data(self):
        """
        Returns:
            (dict) mapping of Players to a bitstring representing the cells they occupy
        """
        return self._data

    @property
    def length(self):
        """
        Returns:
            (int) the side length of the GameState's grid
        """
        return self._length

    @property
    def turn(self):
        """
        Returns:
            (Player) the player whose turn it is
        """
        return self._turn

    def __init__(self, data, length, turn):
        """
        Creates a game state from two 3x3 bit-matrices.
        Validates the state upon creation so that it is not possible to have an invalid state.

        Parameters:
            data (dict) mapping of Players to 3x3 bit-matrix or bitstring representing the cells they occupy
            turn (Player) the Player whose turn it is
        Raises:
            TypeError if any matrix is neither an int nor a tuple or has the wrong dimensions
            RuntimeError if the specified position is not valid
        """
        self._data = {p: matrix_to_bitstring(d) if isinstance(d, tuple) else d for p, d in data.items()}
        self._length = length
        self._turn = turn
        self.validate()

    def __eq__(self, other):
        """
        Parameters:
            other (GameState) the object to compare to
        Returns:
            (bool) True if the two GameStates have the same bitstrings for both players, False otherwise
        """
        return isinstance(other, GameState) and not reduce(lambda acc, pair: acc | pair[0] ^ pair[1], zip(self.data.values()), 0)

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the GameState
        """
        return "\n\t--+---+--\n".join(["\t" + " | ".join([str(self[(r, c)]) for c in range(self.length)]) for r in range(self.length)])

    def __hash__(self):
        """
        Returns:
            (int) a hash of the GameState which depends on both players' bitstrings
        """
        return reduce(lambda acc, bitstring: acc << self.length ** 2 | bitstring, self.data.values(), 0)

    def __bool__(self):
        """
        Returns:
            (bool) True if the GameState represents an empty board, False otherwise
        """
        return bool(reduce(lambda acc, bitstring: acc | bitstring, self.data.values(), 0))

    def __nonzero__(self):
        """Python 2 compatibility."""
        return self.__bool__()

    def __getitem__(self, cell):
        """
        Returns the single-character representation of the player occupying one of the cells in the GameState.

        Parameters:
            cell (tuple) the coordinates of the cell to access
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            IndexError if the specified indices are not within the valid range
        Returns:
            (Player) the Player occupying the specified cell
        """
        if not isinstance(cell, tuple):
            raise TypeError("Cell must be a tuple.")
        if len(cell) != 2:
            raise TypeError("Exactly two coordinates must be specified.")
        for coordinate in cell:
            if not isinstance(coordinate, int):
                raise TypeError("Each coordinate must be an integer.")
            if coordinate not in range(self.length):
                raise IndexError("{} is out of range.".format(coordinate))

        bitmask = 1 << (self.length ** 2 - cell[0] * self.length - cell[1] - 1)
        for player, bitstring in self.data.items():
            if bitstring & bitmask:
                return player
        return self.EMPTY_CELL

    def is_grid_filled(self):
        """
        Determines whether the GameState's grid is completely filled and no further moves are possible.

        Returns:
            (bool) True if the grid is filled, False otherwise
        """
        return not (((1 << self.length ** 2) - 1) ^ reduce(lambda acc, bitstring: acc | bitstring, self.data.values(), 0))

    def get_winning_sequences(self):
        """
        Finds winning sequences in the GameState for all players.

        Returns:
            (dict) mapping winning player to list of winning sequences which are lists of coordinate tuples
                   (in some cases there could be multiple sequences for the same player)
        """
        result = {}
        for player, bitstring in self.data.items():
            sequences = [occupied_cells(s, self.length) for s in filter(lambda s: not (bitstring & s ^ s), self.winning_sequences)]
            if sequences:
                result[player] = sequences
        return result

    def validate(self):
        """
        Determines whether the GameState represents a valid Tic-Tac-Toe position.
        A valid Tic-Tac-Toe position satisfies the following conditions:
            1) the player whose turn it is has a bitstring in the data
            2) only one player occupies each cell
            3) the difference in the number of cells occupied by each player is at most one
            4) at most one player has a winning sequence
            5) if a player has a winning sequence, it is the next player's turn

        Raises:
            RuntimeError if any of these conditions are not satisfied
        Returns: (None)
        """
        if self.turn not in self.data:
            raise RuntimeError("Turn is invalid.")
        for pair in combinations(self.data.values(), 2):
            if pair[0] & pair[1]:
                raise RuntimeError("Cell is occupied by multiple players.")
            if abs(bit_sum(pair[0]) - bit_sum(pair[1])) > 1:
                raise RuntimeError("Cell distribution is invalid.")
        sequences = self.get_winning_sequences()
        if len(sequences) > 1:
            raise RuntimeError("Multiple players have won.")
        if sequences and next(iter(sequences)).next != self.turn:
            raise RuntimeError("Turn doesn't correspond to winning player.")

    def get_cell_states(self):
        """
        Generates a dictionary that maps the coordinates of each cell in the GameState to its state.

        Returns:
            (dict) map of cell coordinates to the string representation of its state
        """
        states = {c: p for p, b in self.data.items() for c in occupied_cells(b, self.length)}
        states.update({c: self.EMPTY_CELL for c in self.get_empty_cells()})
        return states

    def get_empty_cells(self):
        """
        Generates a list of the coordinates of all unoccupied cells in the GameState.

        Returns:
            (list) tuples of the coordinates of all unoccupied cells
        """
        return occupied_cells(((1 << self.length ** 2) - 1) ^ reduce(lambda acc, bitstring: acc | bitstring, self.data.values(), 0), self.length)

    def generate_successor(self, cell):
        """
        Generates a new GameState which represents the position after one move is made from the GameState.

        Parameters:
            cell (tuple) the coordinates of the cell to be updated
        Raises:
            TypeError if the cell parameter is not a tuple or has the wrong length
            IndexError if the specified indices are not within the valid range
            ValueError if the cell is already occupied
        Returns:
            (GameState) the successor state
        """
        if cell not in self.get_empty_cells():
            raise ValueError("{} is already occupied.".format(cell))

        bitmask = 1 << (self.length ** 2 - cell[0] * self.length - cell[1] - 1)
        newdata = copy(self.data)
        newdata[self.turn] |= bitmask
        return GameState(newdata, self.length, self.turn.next)


class Game(object):
    """Object which represents a Tic-Tac-Toe game."""

    @property
    def players(self):
        """
        Returns:
            (list) all of the players participating in the Game
        """
        return self._players

    @players.setter
    def players(self, value):
        """
        Parameters:
            value (list) all of the players participating in the Game
        """
        players = deepcopy(value)
        for i in range(len(players)):
            players[i - 1].next = players[i]
        self._players = players

    @property
    def length(self):
        """
        Returns:
            (int) the side length of the grid in the Game
        """
        return self.state.length

    @property
    def turn(self):
        """
        Returns:
            (Player) the player whose turn it is in the Game
        """
        return self.state.turn

    @property
    def state(self):
        """
        Returns:
            (GameState) the state of the Game
        """
        return self._state

    @state.setter
    def state(self, value):
        """
        Changes the Game's GameState.

        Parameters:
            value (GameState) the new state
        """
        self._state = value

    def __init__(self, length=3, players=[Player('X'), Player('O')]):
        """
        Creates a new game with an empty board and the specified players.
        Players will take turns in the order specified.

        Parameters:
            length (int) the side length of the grid in the Game
            players (list) Player objects that will participate in the Game
        """
        self.players = players
        self.state = GameState({p: 0 for p in self.players}, length, self.players[0])

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the Game
        """
        result = "A {}x{} game of Tic-Tac-Toe\n".format(self.length, self.length) + str(self.state)
        try:
            sequences = self.get_winning_sequences()
        except RuntimeError:  # Game is not over
            return result
        else:
            return result + ("\n{} Wins!".format(str(sequences[0])) if sequences[0] else "\nDraw!")

    def __bool__(self):
        """
        Returns:
            (bool) True if the Game is not over, False otherwise
        """
        return not self.state.is_grid_filled() and not self.state.get_winning_sequences()

    def __nonzero__(self):
        """Python 2 compatibility."""
        return self.__bool__()

    def get_cell_states(self):
        """
        Generates a dictionary that maps the coordinates of each cell to its state.

        Returns:
            (dict) map of cell coordinates to the string representation of its state
        """
        return self.state.get_cell_states()

    def get_winning_sequences(self):
        """
        Generates a list of winning sequences and determines the winning player.

        Raises:
            RuntimeError if the game is not over
        Returns:
            (tuple)
                (Player) The winning player or None if the game is a draw
                (list) of winning sequences which are lists of coordinate tuples (in some cases there could be multiple sequences)
        """
        if self:
            raise RuntimeError("Game is not over.")

        sequences = self.state.get_winning_sequences()
        return next(iter(sequences.items())) if sequences else None

    def get_legal_actions(self):
        """
        Generates a list of legal moves (unoccupied cells).

        Returns:
            (list) tuples of the coordinates of all unoccupied cells
        """
        return self.state.get_empty_cells() if self else []

    def make_move(self, cell):
        """
        Makes a move for the player whose turn it currently is.

        Parameters:
            cell (tuple) the coordinates of the cell to be updated
        Returns:
            (bool) True if the move is completed successfully, False otherwise
        """
        try:
            new = self.state.generate_successor(cell)
        except (TypeError, IndexError, ValueError, RuntimeError):
            return False
        self.state = new
        return True


if __name__ == '__main__':
    g = Game()
    print(g)
    for cell in [(0, 0), (1, 0), (1, 1), (2, 2), (0, 1), (0, 2), (2, 1)]:
        g.make_move(cell)
        print(g)
