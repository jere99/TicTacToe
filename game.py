from copy import copy
from functools import reduce
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

    return reduce(lambda acc, cell: acc << 1 | cell, itertools.chain.from_iterable(grid))


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


class Player:
    """Wrapper object that represents a player with a unique representation."""

    def __init__(self, representation):
        """
        Creates a Player with a unique string representation.

        Parameters:
            (str) representation a single ascii character that does not belong to any existing player
        Raises:
            TypeError if the string representation is invalid
        """
        try:
            ord(representation)
        except TypeError:
            raise TypeError("The player representation must be a single ascii character.")
        self.representation = representation
        self.next = None

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

    def set_next(self, other):
        """
        Sets another Player to follow the Player in the turn order.

        Parameters:
            other (Player) a Player who should go next
        """
        self.next = other

    def get_next(self):
        """
        Sets another Player to follow the Player in the turn order.

        Raises:
            RuntimeError if the next Player has not been set
        Returns:
            (Player) a Player who should go next
        """
        if not self.next:
            raise RuntimeError("No next player has been set.")
        return self.next


class GameState:
    """Immutable object which represents the state of a Tic-Tac-Toe game."""

    EMPTY_CELL = ' '

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

    def __init__(self, data, turn):
        """
        Creates a game state from two 3x3 bit-matrices.
        Validates the state upon creation so that it is not possible to have an invalid state.

        Parameters:
            data (dict) mapping of Players to 3x3 bit-matrix or bitstring representing that player's cells
            turn (Player) the Player whose turn it is
        Raises:
            TypeError if any matrix is neither an int nor a tuple or has the wrong dimensions
            RuntimeError if the specified position is not valid
        """
        self.data = {p: d if isinstance(d, int) else matrix_to_bitstring(d) for p, d in data.items()}
        self.turn = turn
        self.validate()

    def __eq__(self, other):
        """
        Parameters:
            other (GameState) the object to compare to
        Returns:
            (bool) True if the two GameStates have the same bitstrings for both players, False otherwise
        """
        return isinstance(other, GameState) and not reduce(lambda acc, pair: acc | pair[0] ^ pair[1], zip(self.data.values()))

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the GameState
        """
        return "\n\t--+---+--\n".join(map(lambda row: "\t" + " | ".join(map(lambda column: str(self[(row, column)]), range(3))), range(3)))

    def __hash__(self):
        """
        Returns:
            (int) a hash of the GameState which depends on both players' bitstrings
        """
        return reduce(lambda acc, bitstring: acc << 9 | bitstring, self.data.values())

    def __bool__(self):
        """
        Returns:
            (bool) True if the GameState represents an empty board, False otherwise
        """
        return bool(reduce(lambda acc, bitstring: acc | bitstring, self.data.values()))

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
            if coordinate not in range(3):
                raise IndexError(coordinate + " is out of range.")

        bitmask = 1 << (8 - (cell[0] * 3 + cell[1]))
        for player, bitstring in self.data.items():
            if bitstring & bitmask:
                return player
        return self.EMPTY_CELL

    def get_turn(self):
        """
        Returns:
            (Player) the player whose turn it is
        """
        return self.turn

    def is_grid_filled(self):
        """
        Determines whether the GameState's grid is completely filled and no further moves are possible.

        Returns:
            (bool) True if the grid is filled, False otherwise
        """
        return not (0x1FF ^ reduce(lambda acc, bitstring: acc | bitstring, self.data.values()))

    def get_winning_sequences(self):
        """
        Finds winning sequences in the GameState for all players.

        Returns:
            (dict) mapping winning player to list of winning sequences which are lists of coordinate tuples
                   (in some cases there could be multiple sequences for the same player)
        """
        result = {}
        for player, bitstring in self.data.items():
            sequences = [occupied_cells(s) for s in filter(lambda s: not (bitstring & s ^ s), self.WINNING_SEQUENCES)]
            if sequences:
                result[player] = sequences
        return result

    def validate(self):
        """
        Determines whether the GameState represents a valid Tic-Tac-Toe position.
        A valid Tic-Tac-Toe position satisfies the following conditions:
            1) only one player occupies each cell
            2) the difference in the number of cells occupied by each player is at most one
            3) at most one player has a winning sequence
            4) if a player has a winning sequence, it is the next player's turn

        Raises:
            RuntimeError if any of these conditions are not satisfied
        Returns: (None)
        """
        for pair in itertools.combinations(self.data.values(), 2):
            if pair[0] & pair[1]:
                raise RuntimeError("Cell is occupied by multiple players.")
            if abs(bit_sum(pair[0]) - bit_sum(pair[1])) > 1:
                raise RuntimeError("Cell distribution is invalid.")
        sequences = self.get_winning_sequences()
        if len(sequences) > 1:
            raise RuntimeError("Multiple players have won.")
        if sequences and next(iter(sequences)).get_next() != self.turn:
            raise RuntimeError("Turn doesn't correspond to winning player.")

    def get_cell_states(self):
        """
        Generates a dictionary that maps the coordinates of each cell in the GameState to its state.

        Returns:
            (dict) map of cell coordinates to the string representation of its state
        """
        states = {c: p for p, b in self.data.items() for c in occupied_cells(b)}
        states.update({c: self.EMPTY_CELL for c in self.get_empty_cells()})
        return states

    def get_empty_cells(self):
        """
        Generates a list of the coordinates of all unoccupied cells in the GameState.

        Returns:
            (list) tuples of the coordinates of all unoccupied cells
        """
        return occupied_cells(0x1FF ^ reduce(lambda acc, bitstring: acc | bitstring, self.data.values()))

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
            raise ValueError(cell + " is already occupied.")

        bitmask = 1 << (8 - (cell[0] * 3 + cell[1]))
        newdata = copy(self.data)
        newdata[self.turn] |= bitmask
        return GameState(newdata, self.turn.get_next())


class Game:
    """Object which represents a Tic-Tac-Toe game."""

    EMPTY_GRID = ((0, 0, 0), (0, 0, 0), (0, 0, 0))

    def __init__(self, players=[Player('X'), Player('O')]):
        """
        Creates a new game with an empty board and the specified players.
        Players will take turns in the order specified.

        Parameters:
            players (list) Player objects that will participate in the Game
        """
        for i in range(len(players)):
            players[i - 1].set_next(players[i])
        self.players = copy(players)
        self.state = GameState({p: self.EMPTY_GRID for p in players}, players[0])

    def __str__(self):
        """
        Returns:
            (str) human-readable representation of the Game
        """
        result = "A 3x3 game of Tic-Tac-Toe\n" + str(self.state)
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

    def get_players(self):
        """
        Returns:
            (list) all of the players participating in the Game
        """
        return self.players

    def get_turn(self):
        """
        Returns:
            (Player) the player whose turn it is
        """
        return self.state.get_turn()

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
