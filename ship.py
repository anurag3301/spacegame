import math
import pygame as pygame
import pygame.font
import os as os
from enum import Enum
from laser import Laser
import datetime
import copy

script_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = os.path.join(script_dir, 'media')

class Pos:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

class Direction(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4

class DirectionQuant():
    def __init__(self):
        self.reset()

    def reset(self):
        self.up:float = 0
        self.down:float = 0
        self.right:float = 0
        self.left:float = 0
    
    def new_pos(self, pos:Pos, speed:int):
        pos = copy.deepcopy(pos)
        pos.x += self.right * speed
        pos.x -= self.left * speed
        pos.y += self.down * speed
        pos.y -= self.up * speed
        return pos


class Ship:
    def __init__(self, pos:Pos, speed:int, asset_path:str, screen, laser:Laser, max_health:int):
        self.size = 100
        self.pos:Pos = pos
        self.speed:int = speed
        self.texture = pygame.image.load(os.path.join(media_dir, asset_path)) 
        self.texture_size = (self.size, self.texture.get_height()/(self.texture.get_width()/self.size))
        self.texture = pygame.transform.scale(self.texture, self.texture_size)
        self.angle:float = 0
        self.moveDirection:DirectionQuant = DirectionQuant()
        self.screen = screen
        self.laser:Laser = laser
        self.max_health = max_health
        self.health = max_health
        font_path = os.path.join(media_dir, 'PIXY.ttf')
        self.font = pygame.font.Font(font_path, 24)

    def fire(self):
        self.laser.fire(copy.deepcopy(self.pos), self.angle, self.screen)

    def move(self):
        self.pos = self.moveDirection.new_pos(self.pos, self.speed)

    def touchingWall(self):
        walls = []
        window = self.screen.get_rect()
        if self.pos.x <= 0:
            walls.append(Direction.LEFT)
        if self.pos.y <= 0:
            walls.append(Direction.UP)
        if self.pos.x >= window.width:
            walls.append(Direction.RIGHT)
        if self.pos.y >= window.height:
            walls.append(Direction.DOWN)

        return walls

    def hit_ship(self, ship_list):
        for ship in ship_list:
            self.laser.hit_ship(ship) 

    def draw(self):
        self.laser.move_and_draw(self.screen)

        rotated_ship = pygame.transform.rotate(self.texture, self.angle)
        new_rect = rotated_ship.get_rect(center=(self.pos.x, self.pos.y))
        rotated_ship.set_alpha(255)
        self.screen.blit(rotated_ship, new_rect.topleft)

    def healthbar(self):
        bar_width = 100
        bar_height = 12
        bar_x = self.pos.x - bar_width / 2
        bar_y = self.pos.y - self.texture.get_height() - 20 

        pygame.draw.rect(self.screen, (50, 50, 50), pygame.Rect(bar_x, bar_y, bar_width, bar_height))

        health_percentage = max(0, self.health / self.max_health)
        if health_percentage > 0.5:
            red = int(255 * (1 - (health_percentage - 0.5) * 2))
            green = 255
        else:
            red = 255
            green = int(255 * (health_percentage * 2))
        colour = (red, green, 0)

        pygame.draw.rect(self.screen, colour, pygame.Rect(bar_x, bar_y, bar_width * health_percentage, bar_height))

        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(bar_x, bar_y, bar_width, bar_height), 2)

        health_text = str(int(self.health))
        text_surf = self.font.render(health_text, True, colour)
        text_rect = text_surf.get_rect(center=(bar_x + bar_width/2, bar_y + bar_height/2))

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            border_surf = self.font.render(health_text, True, (0,0,0))
            border_rect = border_surf.get_rect(center=(text_rect.centerx + dx*2, text_rect.centery + dy*2))
            self.screen.blit(border_surf, border_rect)

        self.screen.blit(text_surf, text_rect)

class PlayerShip(Ship):
    def __init__(self, pos:Pos, speed:int, asset_path:str, screen, laser:Laser, max_health:int, fire_rate:int, selected_weapon=0):
        super().__init__(pos, speed, asset_path, screen, laser, max_health)
        self.lastFire = 0
        self.fire_rate = fire_rate
        self.selected_weapon = 0
        self.weapon_sounds = [pygame.mixer.Sound(os.path.join(media_dir, f'weapon{i}.mp3')) for i in range(4)]

    def eval_input(self, key, mouse):
        self.moveDirection.reset()
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.moveDirection.left = 1
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.moveDirection.right = 1
        if key[pygame.K_UP] or key[pygame.K_w]:
            self.moveDirection.up = 1
        if key[pygame.K_DOWN] or key[pygame.K_s]:
            self.moveDirection.down= 1

        mouse_x, mouse_y = mouse
        dx, dy = mouse_x - (self.pos.x), mouse_y - (self.pos.y)
        desiredAngle = math.degrees(math.atan2(-dy, dx)) 
        angleDiff = (desiredAngle - self.angle + 180) % 360 - 180
        self.angle += angleDiff / 10
        
    def get_timestamp(self):
        return int(datetime.datetime.now().timestamp()*1000)

    def fire(self):
        diff = self.get_timestamp() - self.lastFire
        if diff >= 1000/self.fire_rate:
            self.laser.fire(copy.deepcopy(self.pos), self.angle, self.screen)
            self.lastFire = self.get_timestamp()
            self.weapon_sounds[self.selected_weapon].play()


class EnemyShip(Ship):
    def __init__(self, pos:Pos, speed:int, asset_path:str, screen, laser:Laser, max_health:int, fire_rate:int):
        super().__init__(pos, speed, asset_path, screen, laser, max_health)
        self.moveDirection = DirectionQuant()
        self.lastFire = self.get_timestamp()
        self.fire_rate = fire_rate

    def get_timestamp(self):
        return int(datetime.datetime.now().timestamp()*1000)

    def generateMove(self, playerShip:PlayerShip):
        self.moveDirection.reset()
        dx = playerShip.pos.x - self.pos.x
        dy = playerShip.pos.y - self.pos.y

        distance = math.sqrt(dx**2 + dy**2)
        mx = dx/distance
        my = dy/distance
        if distance < 100: 
            mx = -300/distance*mx
            my = -300/distance*my
        elif distance < 200: 
            mx = -150/distance*mx
            my = -150/distance*my
        elif distance < 250:
            mx, my = 0, 0
        elif distance < 500:
            mx = 250/distance*mx
            my = 250/distance*my
        elif distance < 700:
            mx = 450/distance*mx
            my = 450/distance*my
        if mx > 0:
            self.moveDirection.right = mx
        else:
            self.moveDirection.left = abs(mx)
        if my > 0:
            self.moveDirection.down = my
        else:
            self.moveDirection.up = abs(my)

        desiredAngle = math.degrees(math.atan2(-dy, dx)) 
        angleDiff = (desiredAngle - self.angle + 180) % 360 - 180
        self.angle += angleDiff / 10

    def fire(self):
        diff = self.get_timestamp() - self.lastFire
        if diff >= 1000/self.fire_rate:
            self.laser.fire(copy.deepcopy(self.pos), self.angle, self.screen)
            self.lastFire = self.get_timestamp()
