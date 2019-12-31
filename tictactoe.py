import itertools

import game

WINDOW_PADDING_FACTOR = 0.1
CELL_PADDING_FACTOR = 0.2


def setup():
    this.surface.setTitle("Tic-Tac-Toe")
    fullScreen()

    global SIZE, CELL_SIZE, INTERNAL_CELL_SIZE, X_MARGIN, Y_MARGIN
    SIZE = min(width, height) * (1 - WINDOW_PADDING_FACTOR)
    CELL_SIZE = SIZE / 3
    INTERNAL_CELL_SIZE = CELL_SIZE * (1 - CELL_PADDING_FACTOR)
    X_MARGIN = (width - SIZE) * 0.5
    Y_MARGIN = (height - SIZE) * 0.5

    global tictactoe, COLOR_SCHEME, ALPHA_REDUCTION
    tictactoe = game.Game([game.Player('1'), game.Player('2'), game.Player('3'), game.Player('4')])
    players = tictactoe.get_players()
    colorMode(HSB, 360, 100, 100)
    base_hue = random(360)
    COLOR_SCHEME = {p: color((base_hue + 360 // len(players) * i) % 360, 100, 50) for i, p in enumerate(players)}
    ALPHA_REDUCTION = color(0, 0, 0, 102)

    # frameRate(1)


def draw():
    background(51)
    translate(X_MARGIN, Y_MARGIN)

    # Draw empty grid
    stroke(255)
    strokeWeight(4)
    for i in range(1, 3):
        line(0, CELL_SIZE * i, width - X_MARGIN * 2, CELL_SIZE * i)
        line(CELL_SIZE * i, 0, CELL_SIZE * i, height - Y_MARGIN * 2)

    # Fill occupied cells
    noStroke()
    for coordinates, state in tictactoe.get_cell_states().items():
        try:
            fill(COLOR_SCHEME[state] - ALPHA_REDUCTION)
        except KeyError:  # Empty cell
            pass
        else:
            ellipse(CELL_SIZE * (coordinates[0] + 0.5), CELL_SIZE * (coordinates[1] + 0.5), INTERNAL_CELL_SIZE, INTERNAL_CELL_SIZE)

    try:
        winner, sequences = tictactoe.get_winning_sequences()
    except (RuntimeError, TypeError):  # No winner
        pass
    else:
        stroke(COLOR_SCHEME[winner])
        strokeWeight(4)
        noFill()
        for coordinates in itertools.chain.from_iterable(sequences):
            ellipse(CELL_SIZE * (coordinates[0] + 0.5), CELL_SIZE * (coordinates[1] + 0.5), INTERNAL_CELL_SIZE, INTERNAL_CELL_SIZE)


def mouseClicked():
    if mouseX > X_MARGIN and mouseX < width - X_MARGIN and mouseY > Y_MARGIN and mouseY < height - Y_MARGIN:
        tictactoe.make_move((int((mouseX - X_MARGIN) // CELL_SIZE), int((mouseY - Y_MARGIN) // CELL_SIZE)))
