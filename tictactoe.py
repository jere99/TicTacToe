import game
import graphics

LENGTH = 3
DIMENSIONALITY = 2

def setup():
    this.surface.setTitle("Tic-Tac-Toe")
    fullScreen()

    global SIZE, CELL_SIZE, X_MARGIN, Y_MARGIN
    SIZE = min(width, height) * 0.9
    X_MARGIN = (width - SIZE) * 0.5
    Y_MARGIN = (height - SIZE) * 0.5
    CELL_SIZE = SIZE / LENGTH

    global tictactoe
    tictactoe = game.Game(LENGTH, DIMENSIONALITY)

def draw():
    background(51)
    stroke(255)
    strokeWeight(4)
    for i in range(1, LENGTH):
        line(X_MARGIN, Y_MARGIN + i * CELL_SIZE, width - X_MARGIN, Y_MARGIN + i * CELL_SIZE)
        line(X_MARGIN + i * CELL_SIZE, Y_MARGIN, X_MARGIN + i * CELL_SIZE, height - Y_MARGIN)

    noStroke()
    for coordinates, player in tictactoe.getFilledCells():
        fill(255, 0, 0, 51) if player == game.CellState.PLAYER1 else fill(0, 0, 255, 51)
        ellipse(X_MARGIN + (coordinates[0] + 0.5) * CELL_SIZE, Y_MARGIN + (coordinates[1] + 0.5) * CELL_SIZE, CELL_SIZE * 0.9, CELL_SIZE * 0.9)

def mouseClicked():
    if mouseX > X_MARGIN and mouseX < width - X_MARGIN and mouseY > Y_MARGIN and mouseY < height - Y_MARGIN:
        tictactoe.makeMove((int((mouseX - X_MARGIN) / CELL_SIZE), int((mouseY - Y_MARGIN) / CELL_SIZE)))
