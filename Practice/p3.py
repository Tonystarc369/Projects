import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

particles = []

class Particle:
    def __init__(self):
        self.x = WIDTH//2
        self.y = HEIGHT//2

        angle = random.uniform(0, math.pi*2)
        speed = random.uniform(2,8)

        self.dx = math.cos(angle)*speed
        self.dy = math.sin(angle)*speed

        self.life = random.randint(60,120)
        self.color = (
            random.randint(100,255),
            random.randint(100,255),
            255
        )

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)),3)

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((5,5,20))

    for _ in range(15):
        particles.append(Particle())

    for p in particles[:]:
        p.update()
        p.draw()

        if p.life <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()