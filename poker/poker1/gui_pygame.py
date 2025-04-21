import pygame
import sys
import os
from game_logic import TexasHoldEmGame

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
RED = (220, 0, 0)
BLUE = (0, 0, 220)
GOLD = (212, 175, 55)
DARK_GREEN = (0, 80, 0)

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120

# Button dimensions
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40


class PygameGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Texas Hold'em Poker")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 36)
        self.game = TexasHoldEmGame()

        # Load card images
        self.card_images = self._load_card_images()
        self.card_back = pygame.image.load(os.path.join("assets", "cards", "back.png")).convert_alpha()
        self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))

        # UI state
        self.selected_action = None

    def _load_card_images(self):
        """Load card images or create colored rectangles if images aren't available"""
        # Check if assets folder exists
        if not os.path.exists("assets/cards"):
            os.makedirs("assets/cards", exist_ok=True)

        cards = {}
        suits = ["C", "D", "H", "S"]  # Clubs, Diamonds, Hearts, Spades
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

        # Try to load from file, or create colored rectangles
        for suit in suits:
            for rank in ranks:
                card_key = rank + suit
                try:
                    img_path = os.path.join("assets", "cards", f"{card_key}.png")
                    if os.path.exists(img_path):
                        img = pygame.image.load(img_path).convert_alpha()
                    else:
                        # Create a rectangle with text as a placeholder
                        img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                        img.fill(WHITE)
                        pygame.draw.rect(img, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)

                        # Add suit color and symbol
                        suit_color = RED if suit in ["D", "H"] else BLACK
                        suit_symbol = {"C": "♣", "D": "♦", "H": "♥", "S": "♠"}[suit]

                        # Add rank text
                        rank_text = rank
                        if rank == "T":
                            rank_text = "10"

                        text_surf = self.font.render(f"{rank_text}{suit_symbol}", True, suit_color)
                        img.blit(text_surf, (10, 10))

                    # Scale to desired size
                    img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                    cards[card_key] = img
                except:
                    # Fallback if loading/creating fails
                    img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                    img.fill(WHITE)
                    cards[card_key] = img

        # Create a card back
        back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        back.fill(BLUE)
        pygame.draw.rect(back, WHITE, (5, 5, CARD_WIDTH - 10, CARD_HEIGHT - 10), 2)
        pygame.draw.rect(back, WHITE, (10, 10, CARD_WIDTH - 20, CARD_HEIGHT - 20), 1)

        # Save the card back for re-use
        pygame.image.save(back, os.path.join("assets", "cards", "back.png"))

        return cards

    def draw_button(self, text, x, y, width, height, inactive_color, active_color, action=None):
        """Draw a clickable button"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        # Check if mouse is over button
        if x < mouse[0] < x + width and y < mouse[1] < y + height:
            pygame.draw.rect(self.screen, active_color, (x, y, width, height))
            if click[0] == 1 and action is not None:
                self.selected_action = action
        else:
            pygame.draw.rect(self.screen, inactive_color, (x, y, width, height))

        text_surf = self.font.render(text, True, BLACK)
        text_rect = text_surf.get_rect()
        text_rect.center = ((x + (width / 2)), (y + (height / 2)))
        self.screen.blit(text_surf, text_rect)

    def draw_card(self, card, x, y):
        """Draw a card at the specified position"""
        if card is None:
            self.screen.blit(self.card_back, (x, y))
        else:
            self.screen.blit(self.card_images[card], (x, y))

    def draw_community_cards(self):
        """Draw the community cards"""
        # Center the cards
        start_x = (SCREEN_WIDTH - (len(self.game.community_cards) * (CARD_WIDTH + 10))) // 2

        for i, card in enumerate(self.game.community_cards):
            self.draw_card(card, start_x + i * (CARD_WIDTH + 10), 200)

    def draw_player_info(self):
        """Draw player information (chips, status, etc.)"""
        # Draw User area (bottom)
        pygame.draw.rect(self.screen, BLUE, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 180, 400, 120))
        text = self.font.render(f"YOU - ${self.game.chips['User']}", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 170))

        # Draw cards if user hasn't folded
        if "User" in self.game.hands:
            for i, card in enumerate(self.game.hands["User"]):
                self.draw_card(card, SCREEN_WIDTH // 2 - 90 + i * (CARD_WIDTH + 10), SCREEN_HEIGHT - 150)
        else:
            text = self.font.render("FOLDED", True, RED)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT - 110))

        # Draw Bot1 area (upper left)
        pygame.draw.rect(self.screen, RED, (50, 50, 200, 120))
        text = self.font.render(f"BOT1 - ${self.game.chips['Bot1']}", True, WHITE)
        self.screen.blit(text, (60, 60))

        # Draw Bot1's cards (face down unless showdown)
        if "Bot1" in self.game.hands:
            if self.game.hand_complete and self.game.current_stage == "river":
                # Show cards at showdown
                for i, card in enumerate(self.game.hands["Bot1"]):
                    self.draw_card(card, 70 + i * (CARD_WIDTH + 10), 90)
            else:
                # Show card backs
                for i in range(2):
                    self.draw_card(None, 70 + i * (CARD_WIDTH + 10), 90)
        else:
            text = self.font.render("FOLDED", True, RED)
            self.screen.blit(text, (130, 110))

        # Draw Bot2 area (upper right)
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 250, 50, 200, 120))
        text = self.font.render(f"BOT2 - ${self.game.chips['Bot2']}", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH - 240, 60))

        # Draw Bot2's cards (face down unless showdown)
        if "Bot2" in self.game.hands:
            if self.game.hand_complete and self.game.current_stage == "river":
                # Show cards at showdown
                for i, card in enumerate(self.game.hands["Bot2"]):
                    self.draw_card(card, SCREEN_WIDTH - 230 + i * (CARD_WIDTH + 10), 90)
            else:
                # Show card backs
                for i in range(2):
                    self.draw_card(None, SCREEN_WIDTH - 230 + i * (CARD_WIDTH + 10), 90)
        else:
            text = self.font.render("FOLDED", True, RED)
            self.screen.blit(text, (SCREEN_WIDTH - 170, 110))

    def draw_game_info(self):
        """Draw game information (pot, dealer, stage)"""
        # Draw the table
        pygame.draw.ellipse(
            self.screen, DARK_GREEN, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        pygame.draw.ellipse(
            self.screen,
            GREEN,
            (SCREEN_WIDTH // 4 + 10, SCREEN_HEIGHT // 4 + 10, SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20),
        )

        # Draw pot
        text = self.big_font.render(f"POT: ${self.game.pot}", True, GOLD)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        # Draw stage
        text = self.font.render(f"Stage: {self.game.current_stage.upper()}", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        # Draw dealer button
        dealer = self.game.players[self.game.dealer_position]
        text = self.font.render(f"Dealer: {dealer}", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        # Draw current message
        if self.game.message:
            text = self.font.render(self.game.message, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 100))

    def draw_action_buttons(self):
        """Draw buttons for player actions"""
        valid_actions = self.game.get_valid_actions()

        # Position the action buttons at the bottom of the screen
        button_y = SCREEN_HEIGHT - 50
        spacing = 20
        total_width = len(valid_actions) * BUTTON_WIDTH + (len(valid_actions) - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        for i, action in enumerate(valid_actions):
            button_x = start_x + i * (BUTTON_WIDTH + spacing)
            self.draw_button(
                action.upper(), button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, GREEN, (0, 200, 0), action
            )

    def update_display(self):
        """Update the game display"""
        # Clear screen
        self.screen.fill(BLACK)

        # Draw game elements
        self.draw_game_info()
        self.draw_community_cards()
        self.draw_player_info()
        self.draw_action_buttons()

        # Update the display
        pygame.display.flip()

    def handle_user_action(self, action):
        """Process the user action"""
        if action == "continue":
            # Continue to next stage if betting is complete
            if self.game.betting_round_complete:
                self.game.play_round()
            # Start new hand if the hand is complete
            elif self.game.hand_complete:
                self.game.start_new_hand()
            return

        # For betting actions, override game's get_user_action and collect bets
        original_get_user_action = self.game.get_user_action
        self.game.get_user_action = lambda: action

        # If fold action, remove user from hands
        if action == "fold":
            if "User" in self.game.hands:
                del self.game.hands["User"]

        # Collect bets for this round
        self.game.collect_bets()

        # Restore original function
        self.game.get_user_action = original_get_user_action

        # If betting is complete and we're not at the end, advance game
        if self.game.betting_round_complete and not self.game.hand_complete:
            self.game.play_round()

    def play_game(self):
        """Main game loop"""
        self.game.start_game()
        running = True

        while running:
            # Always update the display first
            self.update_display()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Process user action if selected
            if self.selected_action:
                action = self.selected_action
                self.selected_action = None

                if action == "quit":
                    running = False
                else:
                    self.handle_user_action(action)

            # Cap the frame rate
            self.clock.tick(30)

        pygame.quit()


def start_game():
    """Start the pygame-based Texas Hold'em game"""
    gui = PygameGUI()
    gui.play_game()
