import game
import graphics

LENGTH = 3
DIMENSIONALITY = 2

MARGIN_CONSTANT = 0.9

def setup():
    this.surface.setTitle("Tic-Tac-Toe")
    fullScreen()

    global SIZE, CELL_SIZE, X_MARGIN, Y_MARGIN
    SIZE = min(width, height) * MARGIN_CONSTANT
    CELL_SIZE = SIZE / LENGTH
    X_MARGIN = (width - SIZE) * 0.5
    Y_MARGIN = (height - SIZE) * 0.5

    global tictactoe
    tictactoe = game.Game(LENGTH, DIMENSIONALITY)

def draw():
    background(51)
    stroke(255)
    strokeWeight(4)
    for i in range(1, LENGTH):
        line(X_MARGIN, Y_MARGIN + i * CELL_SIZE, width - X_MARGIN, Y_MARGIN + i * CELL_SIZE)
        line(X_MARGIN + i * CELL_SIZE, Y_MARGIN, X_MARGIN + i * CELL_SIZE, height - Y_MARGIN)
