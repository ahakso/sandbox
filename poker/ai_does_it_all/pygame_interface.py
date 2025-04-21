import pygame
import os


class PyGameInterface:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Texas Hold'em Poker")

        # Load background image with error handling
        try:
            image_path = os.path.join(
                os.path.dirname(__file__), "assets", "img", "Gemini_Generated_Image_6todfp6todfp6tod.jpeg"
            )
            print(f"Attempting to load image from: {image_path}")
            self.background = pygame.image.load(image_path)
            self.background = pygame.transform.scale(self.background, (1024, 768))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background image: {e}")
            # Create a fallback dark green background
            self.background = pygame.Surface((1024, 768))
            self.background.fill((0, 100, 0))

        # Initialize other game elements
        # ...existing code...

    def draw(self):
        # Draw background first
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()  # Make sure we can see the background

        # Draw other game elements
        # ...existing code...
