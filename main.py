import pygame
import os
import math
from ship import *
from laser import Laser

script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, 'images')

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True


script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, 'images')

ship_laser = Laser(10, os.path.join(images_dir, 'bullet.png'), 10)
ship = PlayerShip(Pos(100, 100), 4, os.path.join(images_dir, 'ship.png'), screen, ship_laser, 1000)
e1ship_laser = Laser(10, os.path.join(images_dir, 'bullet.png'), 10)
e1ship = EnemyShip(Pos(100, 300), 2, os.path.join(images_dir, 'enemy.png'), screen, e1ship_laser, 200, 3)


 
while running:
    # Event handling
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

    e1ship.generateMove(ship)
    e1ship.move()
    e1ship.fire()

    ship.hit_ship([e1ship])

    screen.fill(pygame.Color(20, 23, 36))

    ship.draw()
    e1ship.draw()


    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
