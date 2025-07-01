import pygame
import os
import math
from ship import *
from laser import Laser
import threading
import random

running = True
script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, 'images')
enemy_ships = []
score = 0

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

ship_laser = Laser(10, os.path.join(images_dir, 'bullet.png'), 30)
ship = PlayerShip(Pos(random.randint(0, 1280), random.randint(0, 720)), 4, os.path.join(images_dir, 'ship.png'), screen, ship_laser, 1000)
e1ship_laser = Laser(10, os.path.join(images_dir, 'bullet.png'), 10)
score_font = pygame.font.Font('freesansbold.ttf', 40)


def new_enemy():
    if not running:
        return
    enemy_ships.append(EnemyShip(Pos(random.randint(0, 1280), random.randint(0, 720)), 2, os.path.join(images_dir, 'enemy.png'), screen, e1ship_laser, 200, 1))
    threading.Timer(5, new_enemy).start()

def process_enemy(e1ship):
    e1ship.generateMove(ship)
    e1ship.move()
    e1ship.fire()
    e1ship.hit_ship([ship])
    e1ship.draw()


new_enemy()
 
while running:
    # Event handling
    screen.fill(pygame.Color(20, 23, 36))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ship.fire()

    # Update position
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    ship.eval_input(keys, mouse_pos)
    ship.move()


    ship.hit_ship(enemy_ships)
    ship.draw()

    for enemy_ship in enemy_ships[:]:
        if enemy_ship.health <= 0:
            enemy_ships.remove(enemy_ship)
            score += 100
            continue
        process_enemy(enemy_ship)

    text = score_font.render(str(score), True, (255,0,0), (20, 23, 36))

    textRect = text.get_rect()
    textRect.center = (80, 30)
    screen.blit(text, textRect)

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
