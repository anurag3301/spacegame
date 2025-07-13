import pygame
import os

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
text = None
textRect = None
name = None
nameRect = None

class Button: 
    def __init__(self, color, hoverColor, x, y, width, height, text=''):
        self.color = color
        self.hoverColor = hoverColor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if self.isOver(pygame.mouse.get_pos()):
            pygame.draw.rect(win, self.hoverColor, (self.x, self.y, self.width, self.height), 0)
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        if outline:
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
        
        if self.text != '':
            font = pygame.font.Font(os.path.join(media_dir, 'PIXY.ttf'), 60)
            text = font.render(self.text, 1, (255, 255, 255))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x, y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

def initScreen():
    global text, textRect, name, nameRect
    
    font_path = os.path.join(media_dir, 'PIXY.ttf')
    font = pygame.font.Font(font_path, 80)
    startButton = Button(buttonColor, 500, 520, 280, 80, 'Start!')
    text = font.render("Space Game", True, (255, 0, 0))
    textRect = text.get_rect(center=(640, 60))
    
    score_font = pygame.font.Font(font_path, 40)
    name = score_font.render(f"Sandeep Shenoy", True, (230, 152, 57))
    nameRect = name.get_rect()
    nameRect.center = (640, 60)
    nameRect = name.get_rect(center=(640, 680))

def screenRender():
    screen.fill(pygame.Color(6, 4, 10))
    startButton.draw(screen)
    screen.blit(text, textRect)
    screen.blit(name, nameRect)

buttonColor = (72, 163, 73)
hoverColor = (92, 183, 93)
startButton = Button(buttonColor, hoverColor, 500, 520, 280, 80, 'Start!')
script_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = 'media'