import pygame
import os

TILE_SIZE = 32
LEVEL1_TITLE = "A Dim Forest"
LEVEL1_BACKGROUND = os.path.join('backgrounds', 'forestbackground.png')

LEVEL1_LAYOUT = [
    "................................................................................",
    "################################################################################",
]

def load_tile_images():
    tile_images = {
        "#": pygame.image.load(os.path.join('tiles', 'ground1.png')).convert_alpha(),
        ".": pygame.image.load(os.path.join('tiles', 'grass1.png')).convert_alpha()
    }
    return tile_images

def find_grass_tiles(level_layout, tile_size, screen_height):
    grass_tiles = []
    for y in range(len(level_layout)):
        for x in range(len(level_layout[y])):
            if level_layout[y][x] == ".":  
                y = screen_height - (len(level_layout) - y) * tile_size
                grass_tiles.append((x * tile_size, y))
    return grass_tiles

def main():
    pygame.init()
    screen_width = 960
    screen_height = 540
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(LEVEL1_TITLE)

    background = pygame.image.load(LEVEL1_BACKGROUND).convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))
    tile_images = load_tile_images()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
