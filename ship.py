import math
import pygame as pygame
import os as os
from enum import Enum
from laser import Laser
import datetime
import copy

script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, 'images')

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
        self.texture = pygame.image.load(os.path.join(images_dir, asset_path)) 
        self.texture_size = (self.size, self.texture.get_height()/(self.texture.get_width()/self.size))
        self.texture = pygame.transform.scale(self.texture, self.texture_size)
        self.angle:float = 0
        self.moveDirection:DirectionQuant = DirectionQuant()
        self.screen = screen
        self.laser:Laser = laser
        self.max_health = max_health
        self.health = max_health

    def fire(self):
        self.laser.fire(copy.deepcopy(self.pos), self.angle)

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

        # def blurPos(topleft, amount):
        #     bx, by = topleft
        #     if self.moveDirection == "UP":
        #         by += amount
        #     elif self.moveDirection == "DOWN":
        #         by -= amount
        #     elif self.moveDirection == "RIGHT":
        #         bx -= amount
        #     elif self.moveDirection == "LEFT":
        #         bx += amount
        #     return (bx, by)

        rotated_ship = pygame.transform.rotate(self.texture, self.angle)
        new_rect = rotated_ship.get_rect(center=(self.pos.x, self.pos.y))
        # rotated_ship.set_alpha(64)
        # self.screen.blit(rotated_ship, blurPos(new_rect.topleft, 12))
        # rotated_ship.set_alpha(128)
        # self.screen.blit(rotated_ship, blurPos(new_rect.topleft, 6))
        rotated_ship.set_alpha(255)
        self.screen.blit(rotated_ship, new_rect.topleft)


        health_percentage = self.health / self.max_health * 100
        if health_percentage < 50:
            colour = (255, int(health_percentage*5.1), 0)
        else:
            colour = (int(255-((health_percentage-50)*5.1)), 255, 0)

        hh, hw = 15, 100
        pygame.draw.rect(self.screen, colour, pygame.Rect(self.pos.x-hw/2, self.pos.y-self.texture.get_height(), hw, hh), 2)

        pygame.draw.rect(self.screen, colour, pygame.Rect(self.pos.x-hw/2 + (100-health_percentage)/100*hw, self.pos.y-self.texture.get_height(), health_percentage/100*hw, hh))

class PlayerShip(Ship):
    def __init__(self, pos:Pos, speed:int, asset_path:str, screen, laser:Laser, max_health:int):
        super().__init__(pos, speed, asset_path, screen, laser, max_health)

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


class EnemyShip(Ship):
    def __init__(self, pos:Pos, speed:int, asset_path:str, screen, laser:Laser, max_health:int, fire_rate:int):
        super().__init__(pos, speed, asset_path, screen, laser, max_health)
        self.moveDirection = DirectionQuant()
        self.lastFire = datetime.datetime.now().microsecond
        self.fire_rate = fire_rate

    def generateMove(self, playerShip:PlayerShip):
        self.moveDirection.reset()
        dx = playerShip.pos.x - self.pos.x
        dy = playerShip.pos.y - self.pos.y

        distance = math.sqrt(dx**2 + dy**2)
        mx = dx/distance
        my = dy/distance
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
        self.fireRate = 2
        self.lastFire = datetime.datetime.now()
        elapsed = (datetime.datetime.now() - self.lastFire).total_seconds()
        if elapsed >= 1 / self.fireRate:
            self.laser.fire(copy.deepcopy(self.pos), self.angle)
            self.lastFire = datetime.datetime.now()
