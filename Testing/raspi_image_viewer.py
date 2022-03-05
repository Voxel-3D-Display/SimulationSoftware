import pygame
import time
from voxel_utils import *

pygame.init()

print("Pygame initialized")

display_width = 1920
display_height = 1080

pi_display = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)

crashed = False
i = 1
start = time.time()
num_total_frames = 0

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                crashed = True

    if i >= 39:
        i = 1
        elapsed = time.time() - start
        print("Framerate = {}".format(num_total_frames / elapsed))
    else:
        i += 1
    num_total_frames += 1

    display_image_from_bitmap(pi_display, 'TestClock/', i)

    pygame.display.update()

pygame.quit()
quit()
