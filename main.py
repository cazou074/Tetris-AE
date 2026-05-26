import pygame
import random

# -------------------- INITIALISATION --------------------

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 300, 600

# La fenêtre fait 500px: 300px pour la grille + 200px pour le panneau score/boutons
Screen = pygame.display.set_mode((500, HEIGHT))
pygame.display.set_caption("Tetris AE | Main Menu")

clock = pygame.time.Clock()

BLOCK_SIZE = 30
COLS = WIDTH  // BLOCK_SIZE  # 10
ROWS = HEIGHT // BLOCK_SIZE  # 20

BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)

Score  = 0
perdu  = False

# -------------------- MODE NUIT --------------------
# Actif par défaut; le bouton "N" bascule entre fond noir et fond blanc
NightMode   = True
WindowColor = BLACK
TextColor   = WHITE

# -------------------- PIÈCES --------------------
# Couleur et forme partagent le même index: SHAPES[i] ↔ SHAPES_COLORS[i]
SHAPES_COLORS = [
    ( 53, 177, 222),  # Bleu clair – I
    (246, 250,  25),  # Jaune – O
    (148,  28, 199),  # Violet – T
    (  2,   5, 189),  # Bleu foncé – L
    (236, 126,   0),  # Orange – J
    (255,  10,  10),  # Rouge – Z
    ( 23, 227,  26),  # Vert – S
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
]

# Chaque cellule contient soit 0 (vide), soit le tuple RGB de la pièce qui l'occupe
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


# -------------------- CLASSE PIÈCE --------------------
class Piece:
    def __init__(self):
        self.index = random.randrange(len(SHAPES))
        self.shape = SHAPES[self.index]
        self.color = SHAPES_COLORS[self.index]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        # Transposition + inversion = rotation 90° horaire
        self.shape = list(zip(*self.shape[::-1]))


# -------------------- CLASSE BOUTON --------------------
class Button:
    def __init__(self, x, y, width, height, text, font, fontsize, pos, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(font, fontsize)
        self.pos = (400, 300) if pos is None else pos
        self.action = action
        self.color = WHITE
        self.hover_color = '#666666'
        self.pressed_color = '#333333'
        self.current_color = self.color

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        is_pressed = is_hovered and pygame.mouse.get_pressed()[0]

        # Déclenchement unique sur MOUSEBUTTONDOWN (pas en continu pendant le clic)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_hovered and self.action:
                    self.action()

        if is_pressed:
            self.current_color = self.pressed_color
        elif is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

    def draw(self):
        pygame.draw.rect(Screen, self.current_color, self.rect)
        text_surf = self.font.render(self.text, True, (20, 20, 20))
        Screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))


# -------------------- ACTIONS DES BOUTONS --------------------
def playbutton_click():
    global runningmenu
    runningmenu = False
    pygame.display.set_caption("Tetris AE | Game Mode")

def quitbutton_click():
    pygame.quit()

def nightmodebutton_click():
    global NightMode, WindowColor, TextColor
    if NightMode:
        NightMode = False
        WindowColor = WHITE
        TextColor = BLACK
    else:
        NightMode = True
        WindowColor = BLACK
        TextColor = WHITE


# -------------------- BOUTONS --------------------
playbutton = Button(150, 100, 340, 80, "Play", "Arial", 40, action=playbutton_click, pos=(250, 150))
quitbutton = Button(150, 200, 340, 80, "Quit", "Arial", 40, action=quitbutton_click, pos=(250, 250))
nightmodebutton = Button(475, 575,  20, 20, "N",    "Arial", 40, action=nightmodebutton_click, pos=(250, 550))


# -------------------- LOGIQUE DE JEU --------------------
def valid_position(shape, dx=0, dy=0):
    """Retourne False si le déplacement (dx, dy) sort la pièce de la grille ou la superpose à un bloc."""
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
    """Fige la pièce : enregistre sa couleur dans la grille."""
    for y, row in enumerate(shape.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[shape.y + y][shape.x + x] = shape.color


def clear_lines():
    """Supprime les lignes pleines et retourne leur nombre."""
    global grid
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = ROWS - len(new_grid)
    while len(new_grid) < ROWS:
        new_grid.insert(0, [0] * COLS)
    grid = new_grid
    return lines_cleared


def calculate_score(lines_cleared):
    # Effacer 4 lignes d'un coup (Tetris) vaut bien plus que 4 lignes séparées
    points = {0: 0, 1: 500, 2: 700, 3: 1000, 4: 2000}
    return points.get(lines_cleared, 0)


# -------------------- AFFICHAGE --------------------

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x]:
                pygame.draw.rect(Screen, grid[y][x],
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(Screen, GRAY,
                             (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)


def draw_piece(shapes):
    for y, row in enumerate(shapes.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(Screen, shapes.color,
                                 ((shapes.x + x) * BLOCK_SIZE,
                                  (shapes.y + y) * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE))


# -------------------- BOUCLE PRINCIPALE --------------------
# Architecture en trois phases: menu, partie, game over

piece = Piece()
fall_time = 0
running = True
runningmenu = True

while running:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # ---- Phase 1 : menu principal ----
    if runningmenu:
        Screen.fill(BLACK)
        playbutton.update(events)
        playbutton.draw()
        quitbutton.update(events)
        quitbutton.draw()
        nightmodebutton.update(events)
        nightmodebutton.draw()
        pygame.display.update()
        continue  # On court-circuit tout le reste de la boucle tant qu'on est dans le menu

    # ---- Phase 2 : partie ----
    Screen.fill(WindowColor)
    fall_time += clock.get_rawtime()

    # La vitesse de chute augmente progressivement avec le score (plancher à 20 ms)
    delai_chute = max(20, 500 - Score // 20)
    clock.tick(60)

    if fall_time > delai_chute:
        if valid_position(piece, dy=1):
            piece.y += 1
        else:
            lock_piece(piece)
            lines_cleared = clear_lines()
            Score += calculate_score(lines_cleared)
            Score += 100  # Petit bonus fixe par pièce posée
            piece = Piece()
            if not valid_position(piece):  # Grille pleine → game over
                running = False
                perdu = True
        fall_time = 0

    for e in events:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT  and valid_position(piece, dx=-1):
                piece.x -= 1
            if e.key == pygame.K_RIGHT and valid_position(piece, dx=1):
                piece.x += 1
            if e.key == pygame.K_UP:
                piece.rotate()
                if not valid_position(piece):
                    # Si rotation impossible: 3 rotations de plus pour revenir à la position initiale
                    piece.rotate()
                    piece.rotate()
                    piece.rotate()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN] and valid_position(piece, dy=1):
        piece.y += 1  # Chute accélérée frame par frame

    # Panneau latéral (à droite de la grille)
    font = pygame.font.SysFont("Arial", 32)
    Screen.blit(font.render("Score :", True, TextColor), (310, 20))
    Screen.blit(font.render(str(Score), True, TextColor), (310, 60))

    draw_grid()
    draw_piece(piece)

    nightmodebutton.update(events)
    nightmodebutton.draw()

    pygame.display.update()


# -------------------- ÉCRAN DE FIN --------------------
# Affiché uniquement si la grille s'est remplie (pas si l'utilisateur ferme la fenêtre)
if perdu:
    fenetre = pygame.display.set_mode((800, 600))
    image_defaite = pygame.image.load('gameover.png').convert_alpha()

    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
        fenetre.blit(image_defaite, (250, 13))
        pygame.display.flip()

pygame.quit()