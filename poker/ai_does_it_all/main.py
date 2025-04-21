#!/usr/bin/env python3
import sys
from game_logic import TexasHoldEmGame


def display_game_state(game):
    # Print game state
    print("\n" + "=" * 50)
    print(f"Stage: {game.current_stage}")

    # Print community cards
    if game.community_cards:
        print(f"Community cards: {', '.join(game.community_cards)}")

    # Print player info
    for player in game.players:
        cards = game.hands.get(player, ["Folded"])
        chips = game.chips[player]
        print(f"{player}: {''.join(cards) if cards != ['Folded'] else 'Folded'} - Chips: ${chips}")

    print(f"Pot: ${game.pot}")
    print(f"Current bet: ${game.current_bet}")
    print("=" * 50)


def main():
    game = TexasHoldEmGame()
    game.start_game()

    while True:
        display_game_state(game)

        # Collect bets for the current stage
        if not game.betting_round_complete:
            game.collect_bets()

        # Process the round and advance to the next stage if betting is complete
        hand_complete = game.play_round()

        # Show results if hand is complete
        if hand_complete:
            print(f"\nHand complete! {game.last_winner} wins ${game.pot}")

            play_again = input("Play another hand? (y/n): ")
            if play_again.lower() != "y":
                break

            game.start_new_hand()


if __name__ == "__main__":
    try:
        # Ask user which interface to use
        print("Choose an interface:")
        print("1) Text-based CLI")
        print("2) Graphical window (requires pygame)")

        choice = input("Enter 1 or 2: ")

        if choice == "1":
            # CLI version
            from gui import start_game

            start_game()
        elif choice == "2":
            # GUI version
            try:
                import pygame
                from gui_pygame import start_game

                start_game()
            except ImportError:
                print("Pygame is not installed. Install it using 'pip install pygame'")
                print("Falling back to CLI version...")
                from gui import start_game

                start_game()
        else:
            print("Invalid choice. Using CLI version...")
            from gui import start_game

            start_game()

    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Game terminated.")
