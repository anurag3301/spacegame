import pygame
import math

class Laser:
	def __init__(self, speed, asset_path, damage):
		self.lasers = []
		self.speed = speed
		self.texture = pygame.image.load(asset_path)
		self.damage = damage

	def fire(self, pos, angle, screen):
		radians = math.radians(angle)
		laser_dx = math.cos(radians) * self.speed
		laser_dy = -math.sin(radians) * self.speed
		self.lasers.append({'pos': pos, 'dir': (laser_dx, laser_dy), 'angle': angle, 'texture': self.texture})

	def move_and_draw(self, screen):
		for laser in self.lasers[:]:
			x, y = laser['pos'].x, laser['pos'].y
			rotated_bullet = pygame.transform.rotate(laser['texture'], laser['angle'])
			new_rect = rotated_bullet.get_rect(center=(x, y))
			laser['pos'].x += laser['dir'][0]
			laser['pos'].y += laser['dir'][1]
			sx, sy = pygame.display.get_window_size()
			if x < -5 or y < -5 or x > sx+5 or y > sy+5:
				self.lasers.remove(laser)
			screen.blit(rotated_bullet, new_rect.topleft)

	def hit_ship(self, ship):
		for laser in self.lasers[:]:
			lx, ly = laser['pos'].x, laser['pos'].y
			sx, sy = ship.pos.x, ship.pos.y
			sh, sw = ship.texture.get_height(), ship.texture.get_width()

			if lx >= sx-sw/2 and lx <= sx+sw/2 and \
				ly >= sy-sh/2 and ly <= sy+sh/2:
				self.lasers.remove(laser)
				ship.health -= self.damage	