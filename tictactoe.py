import itertools

import game

WINDOW_PADDING_FACTOR = 0.1
CELL_PADDING_FACTOR = 0.2


def setup():
    this.surface.setTitle("Tic-Tac-Toe")
    fullScreen()

    global SIZE, CELL_SIZE, INTERNAL_CELL_SIZE, HOVER_CELL_SIZE, X_MARGIN, Y_MARGIN
    SIZE = min(width, height) * (1 - WINDOW_PADDING_FACTOR)
    CELL_SIZE = SIZE / 3
    INTERNAL_CELL_SIZE = CELL_SIZE * (1 - CELL_PADDING_FACTOR)
    HOVER_CELL_SIZE = CELL_SIZE * (1 - 0.5 * CELL_PADDING_FACTOR)
    X_MARGIN = (width - SIZE) * 0.5
    Y_MARGIN = (height - SIZE) * 0.5
    rectMode(CENTER)

    global tictactoe
    tictactoe = game.Game([game.Player('1'), game.Player('2'), game.Player('3'), game.Player('4')])
    players = tictactoe.get_players()

    global COLOR_SCHEME
    colorMode(HSB, 360, 100, 100, 100)
    base_hue = random(360)
    COLOR_SCHEME = {p: color((base_hue + map(i, 0, len(players), 0, 360)) % 360, 100, 50) for i, p in enumerate(players)}


def draw():
    background(0, 0, 20)
    translate(X_MARGIN, Y_MARGIN)

    # Draw empty grid
    stroke(0, 0, 100, 80)
    strokeWeight(4)
    for i in range(1, 3):
        line(0, CELL_SIZE * i, width - X_MARGIN * 2, CELL_SIZE * i)
        line(CELL_SIZE * i, 0, CELL_SIZE * i, height - Y_MARGIN * 2)

    # Highlight hovered cell
    cell = mouse_cell()
    if cell:
        noStroke()
        fill(0, 0, 100, 20)
        rect(CELL_SIZE * (cell[0] + 0.5), CELL_SIZE * (cell[1] + 0.5), HOVER_CELL_SIZE, HOVER_CELL_SIZE, HOVER_CELL_SIZE * 0.05)

    # Fill occupied cells
    noStroke()
    for coordinates, state in tictactoe.get_cell_states().items():
        try:
            fill(COLOR_SCHEME[state])
        except KeyError:  # Empty cell
            pass
        else:
            ellipse(CELL_SIZE * (coordinates[0] + 0.5), CELL_SIZE * (coordinates[1] + 0.5), INTERNAL_CELL_SIZE, INTERNAL_CELL_SIZE)

    try:
        winner, sequences = tictactoe.get_winning_sequences()
    except (RuntimeError, TypeError):  # No winner
        pass
    else:
        base_color = COLOR_SCHEME[winner]
        stroke(0, 0, 100, 40)
        strokeWeight(8)
        noFill()
        for coordinates in itertools.chain.from_iterable(sequences):
            ellipse(CELL_SIZE * (coordinates[0] + 0.5), CELL_SIZE * (coordinates[1] + 0.5), INTERNAL_CELL_SIZE, INTERNAL_CELL_SIZE)


def mousePressed():
    cell = mouse_cell()
    if cell:
        tictactoe.make_move(cell)


def mouse_cell():
    """
    Determines which cell the mouse is currently in.

    Returns:
        (tuple) the coorinates of the current cell, or None if the mouse isn't in a cell
    """
    if mouseX > X_MARGIN and mouseX < width - X_MARGIN and mouseY > Y_MARGIN and mouseY < height - Y_MARGIN:
        return (int((mouseX - X_MARGIN) // CELL_SIZE), int((mouseY - Y_MARGIN) // CELL_SIZE))
    else:
        return None
