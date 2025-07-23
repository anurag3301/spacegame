import pygame
import os
from config import *

class Button:
    def __init__(self, color, hoverColor, x, y, width, height, media_dir, text=""):
        self.color = color
        self.hoverColor = hoverColor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.media_dir = media_dir

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if self.isOver(pygame.mouse.get_pos()):
            pygame.draw.rect(win, self.hoverColor, (self.x, self.y, self.width, self.height), 0)
        else:
            pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        if outline:
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
        
        if self.text != '':
            font = pygame.font.Font(os.path.join(self.media_dir, 'PIXY.ttf'), 60)
            text = font.render(self.text, 1, (255, 255, 255))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x, y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False


class StartScreen:
    def __init__(self, media_dir, screen):
        buttonColor = (72, 163, 73)
        hoverColor = (92, 183, 93)
        font_path = os.path.join(media_dir, "PIXY.ttf")
        font = pygame.font.Font(font_path, 80)
        self.startButton = Button(buttonColor, hoverColor, 500, 520, 280, 80, media_dir, "Start!")
        self.text = font.render("Space Game", True, (255, 0, 0))
        self.textRect = self.text.get_rect(center=(640, 60))
        
        if os.path.exists(highscore_file_path):
            file = open(highscore_file_path, "r")
            highscore = int(file.readline())
            file.close()
        self.highScore = pygame.font.Font(font_path, 40).render(f"High Score: {highscore}", True, (170, 189, 240))
        self.highScoreRect = self.highScore.get_rect(center=(640, 115))

        score_font = pygame.font.Font(font_path, 40)
        self.name = score_font.render(f"Made by Sandeep Shenoy", True, (230, 152, 57))
        self.nameRect = self.name.get_rect()
        self.nameRect.center = (640, 60)
        self.nameRect = self.name.get_rect(center=(640, 680))

        self.ship_image = pygame.image.load(
            os.path.join(media_dir, "shipRender.png")
        ).convert_alpha()
        self.ship_image = pygame.transform.scale(self.ship_image, (600, 350))
        self.ship_rect = self.ship_image.get_rect(center=(640, 280))
        self.screen = screen

    def screenRender(self):
        self.screen.blit(self.ship_image, self.ship_rect)
        self.startButton.draw(self.screen)
        self.screen.blit(self.text, self.textRect)
        self.screen.blit(self.name, self.nameRect)
        self.screen.blit(self.highScore, self.highScoreRect)
