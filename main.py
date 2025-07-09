import pygame
import os
import math
from ship import *
from laser import Laser
import threading
import random
import pygame
import numpy as np
import pygame.surfarray
import asyncio
import time

effects = True


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.init()
pygame.mixer.init()

clock = pygame.time.Clock()

pixelSize = 2

script_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = 'media'
final_surface = None

background = pygame.image.load(os.path.join(media_dir, 'background.png'))
stars = pygame.image.load(os.path.join(media_dir, 'stars.png'))
rotated_stars = pygame.transform.rotate(stars, 20).convert_alpha()
rotated_stars.set_alpha(20)
bg_width = background.get_width()
bg_height = background.get_height()
stars_width = stars.get_width()
stars_height = stars.get_height()
rotated_width = rotated_stars.get_width()
rotated_height = rotated_stars.get_height()

running = True
enemy_ships = []
score = 0
weapon = 0
bg_x = 0
bg_y = 0
damage = [6, 20, 35, 240]
firerate = [20, 6, 4, 0.5]
name = ["Minigun", "Burst Fire", "Laser Cannon", "Plasma Barrel"]

ship_laser = Laser(10, os.path.join(media_dir, f'bullet{weapon}.png'), damage[weapon])
ship = PlayerShip(Pos(random.randint(0, 1280), random.randint(0, 720)), 4, os.path.join(media_dir, 'ship.png'), screen, ship_laser, 1000, firerate[weapon], weapon)
e1ship_laser = Laser(10, os.path.join(media_dir, 'enemybullet.png'), 10)
e2ship_laser = Laser(10, os.path.join(media_dir, 'bullet2.png'), 20)
e3ship_laser = Laser(10, os.path.join(media_dir, 'bullet3.png'), 60)

def scanlines(screen, spacing=3, alpha=128):
    for y in range(0, screen.get_height(), spacing):
        temp_surface = pygame.Surface((screen.get_width(), 1), pygame.SRCALPHA)
        pygame.draw.line(temp_surface, (0, 0, 0, alpha), (0, 0), (screen.get_width(), 0), 1)
        screen.blit(temp_surface, (0, y))

def chromatic_aberration(screen, shift_amount=2): # ChatGPT helped with this function
    arr = pygame.surfarray.array3d(screen)
    red = np.roll(arr[:, :, 0], -shift_amount, axis=0)
    blue = np.roll(arr[:, :, 2], shift_amount, axis=0)
    green = arr[:, :, 1]
    combined = np.dstack((red, green, blue))
    new_surface = pygame.surfarray.make_surface(combined)
    screen.blit(new_surface, (0, 0))

async def new_enemy_loop():
    while running:
        num = random.randint(1, 100)
        if num <= 75:
            enemy_ships.append(EnemyShip1(Pos(random.randint(0, 1280), random.randint(0, 720)), 2, os.path.join(media_dir, f'enemy1.png'), screen, e1ship_laser, random.randint(150, 270), 1))
        elif num <= 90:
            enemy_ships.append(EnemyShip2(Pos(random.randint(0, 1280), random.randint(0, 720)), 2, os.path.join(media_dir, f'enemy2.png'), screen, e2ship_laser, random.randint(150, 270), 1))
        else:
            enemy_ships.append(EnemyShip3(Pos(random.randint(0, 1280), random.randint(0, 720)), 2, os.path.join(media_dir, f'enemy3.png'), screen, e3ship_laser, random.randint(150, 270), 1))
        await asyncio.sleep(5)

def process_enemy(eship):
    eship.generateMove(ship)
    eship.move()
    eship.fire()
    eship.hit_ship([ship])
    eship.draw()

def calc_effect():
    global final_surface, bg_x, bg_y
    bg_x = bg_x + (((ship.pos.x * 0.5) - bg_x) * 0.05)
    bg_y = bg_y + (((ship.pos.y * 0.5) - bg_y) * 0.05)
    stars_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

    for y_mult in range(-2, 3):
        y_pos = y_mult * bg_height
        for i in range(-2, 3): 
            x = i * bg_width
            stars_surface.blit(background, (x - bg_x, y_pos - bg_y))
    
    for y_mult in range(-2, 3):
        y_pos = y_mult * bg_height
        for i in range(-2, 3):
            x = i * bg_width
            center_x = x + stars_width // 2
            center_y = y_pos + stars_height // 2

            blit_x = center_x - rotated_width // 2 - int(bg_x * 0.5)
            blit_y = center_y - rotated_height // 2 - int(bg_y * 0.5)

            stars_surface.blit(rotated_stars, (blit_x, blit_y))
    stars_small_size = (screen.get_width() // 4, screen.get_height() // 4)
    stars_small = pygame.transform.scale(stars_surface, stars_small_size)
    stars_pixelated = pygame.transform.scale(stars_small, (screen.get_width(), screen.get_height()))
    final_surface = stars_pixelated


 
async def main():

    asyncio.create_task(new_enemy_loop())
    effect_tread = threading.Thread(target=calc_effect)
    effect_tread.start()

    start, end = 0, 0
    global running, score, weapon, bg_x, bg_y, ship, enemy_ships, final_surface


    while running:
        # Event handling
        screen.fill(pygame.Color(20, 23, 36))
        score += 0.025

        if effects and final_surface:
            screen.blit(final_surface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    weapon = 0
                    pygame.mixer.Sound(os.path.join(media_dir, 'switch.ogg')).play()
                elif event.key == pygame.K_2:
                    weapon = 1
                    pygame.mixer.Sound(os.path.join(media_dir, 'switch.ogg')).play()
                elif event.key == pygame.K_3:
                    weapon = 2
                    pygame.mixer.Sound(os.path.join(media_dir, 'switch.ogg')).play()
                elif event.key == pygame.K_4:
                    weapon = 3
                    pygame.mixer.Sound(os.path.join(media_dir, 'switch.ogg')).play()

        ship.laser.damage = damage[weapon]
        ship.fire_rate = firerate[weapon]
        ship.selected_weapon = weapon
        ship.laser.texture = pygame.image.load(os.path.join(media_dir, f'bullet{weapon}.png'))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            ship.fire()

        mouse_pos = pygame.mouse.get_pos()
        ship.eval_input(keys, mouse_pos)
        ship.move()

        ship.hit_ship(enemy_ships)
        ship.draw()

        if ship.health <= 0:
            running = False
            screen.fill(pygame.Color(6, 4, 10))
            game_over_font = pygame.font.Font(os.path.join(media_dir, 'PIXY.ttf'), 80)
            game_over_text = game_over_font.render("GAME OVER.", True, (255, 0, 0))
            
            font_path = os.path.join(media_dir, 'PIXY.ttf')
            score_font = pygame.font.Font(font_path, 40)
            text = score_font.render(f"Final Score: {int(score)}", True, (230, 152, 57))
            pygame.mixer.Sound(os.path.join(media_dir, 'gameOver.ogg')).play()
            textRect = text.get_rect()
            textRect.center = (640, 60)
            screen.blit(text, textRect)
            text_rect = game_over_text.get_rect(center=(640, 360))
            screen.blit(game_over_text, text_rect)

            pygame.display.flip()

            pygame.time.delay(3000)
            break # So the game quits after 3 seconds

        for enemy_ship in enemy_ships[:]:
            if enemy_ship.health <= 0:
                enemy_ships.remove(enemy_ship)
                score += 100
                pygame.mixer.Sound(os.path.join(media_dir, 'explosion.ogg')).play()
                continue
            process_enemy(enemy_ship)

        font_path = os.path.join(media_dir, 'PIXY.ttf')
        score_font = pygame.font.Font(font_path, 40)
        text = score_font.render(f"Score: {int(score)}", True, (230, 152, 57))
        
        textRect = text.get_rect()
        textRect.center = (640, 60)
        screen.blit(text, textRect)

        weapon_font = pygame.font.Font(font_path, 30)
        weapon_text = weapon_font.render(f"Weapon: {name[weapon]} (1-4 to switch)", True, (123, 172, 224))

        weaponRect = weapon_text.get_rect()
        weaponRect.center = (640, 680)
        screen.blit(weapon_text, weaponRect)

        if effects:
            small_size = (screen.get_width() // pixelSize, screen.get_height() // pixelSize)
            small_surface = pygame.transform.scale(screen, small_size)
            pixelated_surface = pygame.transform.scale(small_surface, screen.get_size())
            screen.blit(pixelated_surface, (0, 0))
            scanlines(screen)

        for enemy_ship in enemy_ships:
            enemy_ship.healthbar()
        ship.healthbar()
        chromatic_aberration(screen)
        FPS_font = pygame.font.Font(font_path, 30)
        fps_text = FPS_font.render(f"FPS: {int(clock.get_fps())}", True, (123, 172, 224))

        fpsRect = fps_text.get_rect()
        fpsRect.center = (80, 680)
        screen.blit(fps_text, fpsRect)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    effect_tread.join()

    pygame.quit()

asyncio.run(main())