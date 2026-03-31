import pygame
import random

# -------------------- INITIALISATION --------------------

pygame.init()  # Démarre tous les modules de pygame (affichage, son, clavier, etc.)

# Dimensions de la fenêtre de jeu en pixels
WIDTH, HEIGHT = 300, 600
PlaySurface = pygame.display.set_mode((WIDTH, HEIGHT))          # Crée la fenêtre principale du jeu (Zone de jeux)
Screen = pygame.display.set_mode((500, 600))          # Recrée la fenêtre avec une largeur plus grande (remplace la précédente)

clock = pygame.time.Clock()  # Crée une horloge pour contrôler la vitesse du jeu (FPS)

# Taille d'une case de la grille en pixels
BLOCK_SIZE = 30
COLS = WIDTH // BLOCK_SIZE   # Nombre de colonnes : 300 // 30 = 10
ROWS = HEIGHT // BLOCK_SIZE  # Nombre de lignes : 600 // 30 = 20

# Définition des couleurs en format RGB (Rouge, Vert, Bleu)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Variables de jeu (non encore utilisées dans cette version)
Score = 0
Speed = 0

# -------------------- FORMES DES PIÈCES --------------------
# Chaque pièce est représentée par une liste de listes :
# 1 = case occupée, 0 = case vide
SHAPES = [
    [[1, 1, 1, 1]],           # Barre (I)
    [[1, 1], [1, 1]],         # Carré (O)
    [[0, 1, 0], [1, 1, 1]],   # Podium (T)
    [[1, 0, 0], [1, 1, 1]],   # Forme L
    [[0, 0, 1], [1, 1, 1]],   # Forme L inversé (J)
    [[1, 1, 0], [0, 1, 1]],   # Forme Z
    [[0, 1, 1], [1, 1, 0]]    # Forme Z inversé (S)
]

# -------------------- GRILLE DE JEU --------------------
# La grille est une liste de ROWS lignes, chacune contenant COLS valeurs :
# 0 = case vide, 1 = case occupée par un bloc posé
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


# -------------------- CLASSE PIÈCE --------------------
class Piece:
    def __init__(self):
        # Choisit une forme aléatoire parmi celles définies dans SHAPES
        self.shape = random.choice(SHAPES)
        # Positionne la pièce horizontalement au centre de la grille
        self.x = COLS // 2 - len(self.shape[0]) // 2
        # La pièce apparaît tout en haut de la grille
        self.y = 0

    def rotate(self):
        # Effectue une rotation de 90° dans le sens horaire
        # zip(*self.shape[::-1]) retourne les colonnes de bas en haut comme nouvelles lignes
        self.shape = list(zip(*self.shape[::-1]))

# -------------------- CLASSE BOUTTON --------------------

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = '#ffffff'
        self.hover_color = '#666666'
        self.pressed_color = '#333333'
        self.current_color = self.color

    def process(self):
        mouse_pos = pygame.mouse.get_pos()
        # Hover effect
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            # Check for click
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                self.current_color = self.pressed_color
                if self.action:
                    self.action()
        else:
            self.current_color = self.color

        # Draw button
        pygame.draw.rect(Screen, self.current_color, self.rect)
        text_surf = font.render(self.text, True, (20, 20, 20))
        text_rect = text_surf.get_rect(center=self.rect.center)
        Screen.blit(text_surf, text_rect)

# -------------------- FONCTIONS BOUTTON --------------------

def playbutton_click():
    global runningmenu
    runningmenu = False
    global PlaySurface
    PlaySurface = pygame.display.set_mode((300, 600))    # recrée la fenêtre principale du jeu (Zone de jeux)
    pygame.display.set_caption("Tetris AE | Game Mode")  # Définit le titre de la fenêtre
    global Screen
    Screen = pygame.display.set_mode((500, 600))         # Recrée la fenêtre avec une largeur plus grande (remplace la précédente)

def quitbutton_click():
    pygame.quit()

# ------------------------ BOUTTONS ------------------------

playbutton = Button(150, 100, 340, 80, "Play", action=playbutton_click)
quitbutton = Button(150, 200, 340, 80, "Quit", action=quitbutton_click)

# -------------------- FONCTIONS UTILITAIRES --------------------

def create_window(Width, Height, WindowName):
    global screen
    screen = pygame.display.set_mode((Width, Height))   # Crée une fenêtre
    pygame.display.set_caption(WindowName)              # Définit le titre de la fenêtre


def valid_position(shape, dx=0, dy=0):
    """
    Vérifie si la pièce peut occuper sa position actuelle + le déplacement (dx, dy).
    Retourne False si la pièce sort de la grille ou chevauche un bloc existant.
    """
    for y, row in enumerate(shape.shape):       # Parcourt chaque ligne de la pièce
        for x, cell in enumerate(row):          # Parcourt chaque cellule de la ligne
            if cell:                            # Si la cellule est occupée (valeur 1).
                new_x = shape.x + x + dx        # Position X cible dans la grille
                new_y = shape.y + y + dy        # Position Y cible dans la grille

                # Vérifie les bords gauche, droit et bas de la grille
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                # Vérifie qu'il n'y a pas déjà un bloc posé à cet endroit
                if new_y >= 0 and grid[new_y][new_x]:
                    return False
    return True  # Aucune collision détectée : la position est valide


def lock_piece(shape):
    """
    Fige la pièce dans la grille en marquant ses cellules avec la valeur 1.
    Appelée quand la pièce ne peut plus descendre.
    """
    for y, row in enumerate(shape.shape):
        for x, cell in enumerate(row):
            if cell:
                grid[shape.y + y][shape.x + x] = 1  # Marque la case comme occupée


def clear_lines():
    """
    Supprime toutes les lignes complètes (sans aucun 0) de la grille,
    puis ajoute des lignes vides en haut pour compenser.
    """
    global grid
    # Garde uniquement les lignes qui contiennent encore au moins un 0 (non complètes)
    grid = [row for row in grid if any(cell == 0 for cell in row)]
    # Remplit les lignes manquantes en haut avec des lignes vides
    while len(grid) < ROWS:
        grid.insert(0, [0 for _ in range(COLS)])
        global Score    # Interagit avec la variable Score qui est global(partout dans le projet)
        Score =+ 1      # Rajoute 1 au Score



def draw_grid():
    """
    Dessine la grille à l'écran:
     - Un carré blanc pour chaque bloc posé (valeur 1).
     - Un contour gris pour chaque case (pour visualiser la grille)
    """
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x]:  # Si la case est occupée, dessine un bloc blanc
                pygame.draw.rect(
                    PlaySurface,
                    WHITE,
                    (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )
            # Dessine le contour gris de chaque case (sur Screen)
            pygame.draw.rect(
                Screen,
                GRAY,
                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                1,  # Épaisseur du contour : 1 pixel
            )


def draw_piece(shapes):
    """
    Dessine la pièce en cours de chute à sa position actuelle dans la grille.
    """
    for y, row in enumerate(shapes.shape):
        for x, cell in enumerate(row):
            if cell:  # Si la cellule de la pièce est occupée
                pygame.draw.rect(
                    PlaySurface,
                    WHITE,
                    ((shapes.x + x) * BLOCK_SIZE,      # Position X en pixels
                     (shapes.y + y) * BLOCK_SIZE,           # Position Y en pixels
                     BLOCK_SIZE,
                     BLOCK_SIZE)
                )


# -------------------- BOUCLE PRINCIPALE DU JEU --------------------

piece = Piece()   # Crée la première pièce
fall_time = 0     # Compteur de temps pour gérer la chute automatique

running = True
runningmenu = True

create_window(640, 480, "Tetris AE | Main Menu")

while running:

    while runningmenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        font = pygame.font.SysFont('Arial', 40)
        playbutton.process()                    # pour fonction voir ligne 97
        quitbutton.process()

        pygame.display.update()



    PlaySurface.fill(BLACK)                        # Efface l'écran en le remplissant de noir
    fall_time += clock.get_rawtime()          # Ajoute le temps écoulé depuis le dernier appel (en ms)
    clock.tick(60)                            # Limite le jeu à 60 FPS

    # --- Chute automatique de la pièce ---
    # Toutes les ~500ms (valeur arbitraire), on fait descendre la pièce d'une case
    if fall_time > 500:
        if valid_position(piece, dy=1):       # Si la pièce peut descendre
            piece.y += 1                      # On la déplace d'une ligne vers le bas
        else:
            # La pièce ne peut plus descendre : on la fige dans la grille.
            lock_piece(piece)
            clear_lines()                     # On vérifie si des lignes sont complètes
            piece = Piece()                   # On génère une nouvelle pièce
            if not valid_position(piece):     # Si la nouvelle pièce est bloquée dès l'apparition...
                running = False              # ... la grille est pleine → fin de partie
        fall_time = 0                         # Réinitialise le compteur de chute

    # --- Gestion des événements (clavier, fermeture de fenêtre) ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT:             # Clic sur la croix de fermeture
            running = False

        if e.type == pygame.KEYDOWN:          # Une touche vient d'être pressée
            if e.key == pygame.K_LEFT and valid_position(piece, dx=-1):
                piece.x -= 1                  # Déplace la pièce vers la gauche
            if e.key == pygame.K_RIGHT and valid_position(piece, dx=1):
                piece.x += 1                  # Déplace la pièce vers la droite
            if e.key == pygame.K_UP:
                piece.rotate()                # Tente une rotation
                if not valid_position(piece): # Si la rotation crée une collision...
                    # ... on annule en effectuant 3 rotations supplémentaires (retour à l'état initial)
                    piece.rotate()
                    piece.rotate()
                    piece.rotate()

    # --- Chute rapide (maintien de la touche BAS) ---
    keys = pygame.key.get_pressed()           # Récupère l'état de toutes les touches en temps réel
    if keys[pygame.K_DOWN] and valid_position(piece, dy=1):
        piece.y += 1                          # Descend la pièce d'une case supplémentaire par frame

    # --- Affichage du score ---
    font = pygame.font.SysFont("Arial", 32)              # Défini la police d'écriture: "Arial" et sa taille: 32
    text = font.render("Score :", True, WHITE)         # Crée une variable avec le texte: "Score :" et sa couleur: WHITE
    Score_text = font.render(str(Score), True, WHITE)       # PS: str(Score) -> Transforme  la valeur de Score en texte

    PlaySurface.blit(text, (300, 0))              # Affiche le texte "Score :" à la position (300, 0)
    PlaySurface.blit(Score_text, (300, 50))       # Affiche le score à la position (300, 50) (en dessous du texte)

    # --- Dessin de la grille et de la pièce ---
    draw_grid()
    draw_piece(piece)

    pygame.display.update()                  # Rafraîchit l'affichage pour montrer les changements

pygame.quit()  # Ferme proprement pygame à la fin de la partie
