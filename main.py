import pygame
import random
#from Menu import *


# -------------------- SETUP -------------------

pygame.init()

# Screen size
WIDTH, HEIGHT = 300, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris AE | Game Mode")
PlaySurface = pygame.display.set_mode((500, 600))

clock = pygame.time.Clock()

# Grid settings
BLOCK_SIZE = 30
COLS = WIDTH // BLOCK_SIZE
ROWS = HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

Score = 0
Speed = 0

# -------------------- SHAPES --------------------
SHAPES = [
    [[1, 1, 1, 1]],  # bar
    [[1, 1], [1, 1]],  # square
    [[0, 1, 0], [1, 1, 1]],  # podium
    [[1, 0, 0], [1, 1, 1]],  # "L"
    [[0, 0, 1], [1, 1, 1]],  # other side "L"
    [[1, 1, 0], [0, 1, 1]],  # "Z" shape
    [[0, 1, 1], [1, 1, 0]]  # other "Z" shape
]


# -------------------- GAME GRID INIT --------------------
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


# -------------------- PIECE CLASS --------------------
class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))


# -------------------- USEFUL FUNCTIONS --------------------
def valid_position(shape, dx=0, dy=0):
    for y, row in enumerate(shape.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = shape.x + x + dx
                new_y = shape.y + y + dy

                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and grid[new_y][new_x]:
                    return False
    return True


def lock_piece(shape):
    for y, row in enumerate(shape.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[shape.y + y][shape.x + x] = 1


def clear_lines():
    global grid
    grid = [row for row in grid if any(cell == 0 for cell in row)]
    while len(grid) < ROWS:
        grid.insert(0, [0 for _ in range(COLS)])


def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x]:
               pygame.draw.rect(
                   screen,
                   WHITE,
                   (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
               )
            pygame.draw.rect(
                PlaySurface,
                GRAY,
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                1,
            )


def draw_piece(shapes):
    for y, row in enumerate(shapes.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    ((shapes.x + x) * BLOCK_SIZE,
                     (shapes.y + y) * BLOCK_SIZE,
                     BLOCK_SIZE,
                     BLOCK_SIZE)
                )


# -------------------- MAIN GAME LOOP --------------------
piece = Piece()
fall_time = 0

running = True
while running:
    screen.fill(BLACK)
    fall_time += clock.get_rawtime()
    clock.tick(60)

    # IDK what time it updates at but 100 seems okay
    if fall_time > 60:         # Arbitrary value here... Wtf now ??
        if valid_position(piece, dy=1):
            piece.y += 1
        else:
            lock_piece(piece)
            clear_lines()
            piece = Piece()
            if not valid_position(piece):
                running = False
        fall_time = 0

    # Inputs and events handling
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT and valid_position(piece, dx=-1):
                piece.x -= 1
            if e.key == pygame.K_RIGHT and valid_position(piece, dx=1):
                piece.x += 1
            if e.key == pygame.K_UP:
                piece.rotate()
                if not valid_position(piece):
                    piece.rotate()
                    piece.rotate()
                    piece.rotate()

    # Fast Downing
    keys = pygame.key.get_pressed()

    if keys[pygame.K_DOWN] and valid_position(piece, dy=1):
        piece.y += 1

    font = pygame.font.SysFont("Arial", 32)
    text = font.render("Score :", True, WHITE)
    screen.blit(text, (300, 0))

    draw_grid()
    draw_piece(piece)
    pygame.display.update()

pygame.quit()
