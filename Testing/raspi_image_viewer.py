import pygame
import time
import os
import sys


def display_images_standard():
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

        img = pygame.image.load(os.path.join(directory, str(i).zfill(5) + '.bmp'))
        pi_display.blit(img, (0, 0))
        del img

        if i >= total_images:
            i = 1
            elapsed = time.time() - start
            print("Framerate = {}".format(num_total_frames / elapsed))
        else:
            i += 1
        num_total_frames += 1

        pygame.display.update()


def display_images_preload():
    crashed = False
    i = 1
    start = time.time()
    num_total_frames = 0

    imgs = list()
    for i in range(total_images):
        imgs.append(pygame.image.load(os.path.join(directory, str(i + 1).zfill(5) + '.bmp')))

    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    crashed = True

        pi_display.blit(imgs[i - 1], (0, 0))

        if i >= total_images:
            i = 1
            elapsed = time.time() - start
            print("Framerate = {}".format(num_total_frames / elapsed))
        else:
            i += 1
        num_total_frames += 1

        pygame.display.update()


pygame.init()

print("Pygame initialized")

display_width = 1920
display_height = 1080
total_images = 10
directory = 'home/pi/Desktop/SimulationSoftware/Testing/StaticTest/'
#directory = 'StaticTest/'

pi_display = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

print("Running Image Viewer")
display_images_preload()

print("Received escape sequence: quitting")
pygame.quit()
quit()
