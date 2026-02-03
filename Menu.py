import pygame
import sys

# Initialize PyGame
pygame.init()

# Screen setup
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris AE | Main Menu")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 40)

# Button class
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
        pygame.draw.rect(screen, self.current_color, self.rect)
        text_surf = font.render(self.text, True, (20, 20, 20))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# Example actions
def playbutton_click():
    print("PlayButton clicked!")
def quitbutton_click():
    print("QuitButton clicked!")

# Create a button
playbutton = Button(150, 100, 340, 80, "Play", action=playbutton_click)
quitbutton = Button(150, 200, 340, 80, "Quit", action=quitbutton_click)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((20, 20, 20))
    playbutton.process()
    quitbutton.process()
    pygame.display.flip()
    clock.tick(60)