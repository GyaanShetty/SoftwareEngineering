import pygame
from game.game_engine import GameEngine

# Initialize pygame/Start application.
# Small mixer buffer = low-latency sound effects. Harmless if audio is unavailable.
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 640, 560
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker - Pygame Version")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game loop
engine = GameEngine(WIDTH, HEIGHT)

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            engine.handle_event(event)
        if engine.quit_requested:
            running = False
            break

        engine.handle_input()
        engine.update()
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
