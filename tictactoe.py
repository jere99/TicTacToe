import game

LENGTH = 3
DIMENSIONALITY = 2

SIZE_CONSTANT = 0.9
CELL_CONSTANT = 0.8

def setup():
    this.surface.setTitle("Tic-Tac-Toe")
    fullScreen()

    global SIZE, CELL_SIZE, X_MARGIN, Y_MARGIN
    SIZE = min(width, height) * SIZE_CONSTANT
    CELL_SIZE = SIZE / LENGTH
    X_MARGIN = (width - SIZE) * 0.5
    Y_MARGIN = (height - SIZE) * 0.5

    global tictactoe
    tictactoe = game.Game(LENGTH, DIMENSIONALITY)

def draw():
    background(51)
    translate(X_MARGIN, Y_MARGIN)
    stroke(255)
    strokeWeight(4)
    for i in range(1, LENGTH):
        line(0, CELL_SIZE * i, width - X_MARGIN * 2, CELL_SIZE  * i)
        line(CELL_SIZE * i, 0, CELL_SIZE  * i, height - Y_MARGIN * 2)

    noStroke()
    for coordinates, player in tictactoe.getFilledCells():
        fill(255, 0, 0, 51) if player == game.CellState.PLAYER1 else fill(0, 0, 255, 51)
        ellipse(CELL_SIZE * (coordinates[0] + 0.5), CELL_SIZE * (coordinates[1] + 0.5), CELL_SIZE * CELL_CONSTANT, CELL_SIZE * CELL_CONSTANT)

    winner, winningCells = tictactoe.getWinner()
    if winner:
        stroke(255, 0, 0) if winner == game.CellState.PLAYER1 else stroke(0, 0, 255)
        strokeWeight(4)
        noFill()
        for coordinates in winningCells:
            ellipse(CELL_SIZE * (coordinates[0] + 0.5), CELL_SIZE * (coordinates[1] + 0.5), CELL_SIZE * CELL_CONSTANT, CELL_SIZE * CELL_CONSTANT)

def mouseClicked():
    if mouseX > X_MARGIN and mouseX < width - X_MARGIN and mouseY > Y_MARGIN and mouseY < height - Y_MARGIN:
        tictactoe.makeMove((int((mouseX - X_MARGIN) / CELL_SIZE), int((mouseY - Y_MARGIN) / CELL_SIZE)))
