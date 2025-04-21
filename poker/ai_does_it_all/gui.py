# GUI for Texas Hold 'Em (Text-based CLI interface)
from game_logic import TexasHoldEmGame
import os

CARD_SUITS = {"C": "♣", "D": "♦", "H": "♥", "S": "♠"}  # Clubs  # Diamonds  # Hearts  # Spades

CARD_RANKS = {
    "A": "A",
    "K": "K",
    "Q": "Q",
    "J": "J",
    "T": "10",
    "9": "9",
    "8": "8",
    "7": "7",
    "6": "6",
    "5": "5",
    "4": "4",
    "3": "3",
    "2": "2",
}


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def format_card(card):
    """Format a card with colored suits."""
    if not card:
        return "🂠"  # Card back symbol

    rank, suit = card[0], card[1]
    suit_symbol = CARD_SUITS[suit]
    rank_symbol = CARD_RANKS[rank]

    # ANSI color codes: red for hearts/diamonds, white for clubs/spades
    if suit in ["H", "D"]:
        return f"\033[91m{rank_symbol}{suit_symbol}\033[0m"
    else:
        return f"{rank_symbol}{suit_symbol}"


def format_cards(cards):
    """Format a list of cards with colored suits."""
    if not cards or len(cards) == 0:
        return "No cards"
    return " ".join(format_card(card) for card in cards)


def display_table(game):
    """Display the poker table with players, community cards, and pot."""
    width = 60
    clear_screen()

    print("\n" + "=" * width)
    print("TEXAS HOLD'EM".center(width))
    print("=" * width)

    # Display community cards
    print("\n" + "-" * width)
    if game.current_stage == "pre-flop":
        print(f"{'Community Cards: [Waiting for flop]':^{width}}")
    else:
        print(f"{'Community Cards:':^{width}}")
        if game.community_cards:  # Make sure we have community cards to display
            cards_display = format_cards(game.community_cards)
            print(f"{cards_display:^{width}}")
        else:
            print(f"{'No community cards yet':^{width}}")
    print("-" * width)

    # Display pot and stage information
    print("\n" + "-" * width)
    print(f"{'Current Pot:':<15}${game.pot}")
    print(f"{'Stage:':<15}{game.current_stage.upper()}")
    print(f"{'Dealer:':<15}{game.players[game.dealer_position]}")
    print("-" * width)

    # Display all players and their chip stacks
    print("\n" + "-" * width)
    print(f"{'PLAYERS':^{width}}")
    print("-" * width)

    for player in game.players:
        if player == "User":
            status = "👤 YOU"
        else:
            status = f"🤖 {player}"

        if player in game.hands:
            active = "Active"
        else:
            active = "Folded"

        chips = f"${game.chips[player]}"
        print(f"{status:<15}{active:<15}{chips}")

    # Display user's hand
    print("\n" + "-" * width)
    if "User" in game.hands:
        print(f"{'Your Hand:':^{width}}")
        user_hand_display = format_cards(game.hands["User"])
        print(f"{user_hand_display:^{width}}")
    else:
        print(f"{'You folded this hand':^{width}}")
    print("-" * width)


def display_action_prompt(game):
    """Display the action prompt for the user."""
    valid_actions = game.get_valid_actions()

    print("\n" + "-" * 60)
    print(f"Your chips: ${game.chips['User']}")

    # Show appropriate bet information based on valid actions
    if "check" in valid_actions:
        print(f"Current bet: ${game.current_bet} (you can check)")
    elif "call" in valid_actions:
        print(f"Current bet to call: ${game.current_bet - game.player_bets['User']}")

    print(f"Valid actions: {', '.join(valid_actions)}")
    print("-" * 60)


def get_user_input(game):
    """Get a valid action from the user."""
    valid_actions = game.get_valid_actions()
    display_action_prompt(game)

    action = ""
    while action not in valid_actions:
        action = input("Your action: ").lower()
        if action not in valid_actions:
            print("Invalid action. Try again.")

    print(f"You chose to {action}")
    return action


def handle_user_turn(game):
    """Handle the user's turn in the game."""
    if "User" not in game.hands:
        # User has folded
        return "continue"

    # Get valid user action
    action = get_user_input(game)

    # If the action is 'continue', just return it
    if action == "continue":
        return action

    # Otherwise, it's a betting action
    # Override the get_user_action method temporarily
    original_get_user_action = game.get_user_action
    game.get_user_action = lambda: action

    # Process the betting round
    game.collect_bets()

    # Restore the original method
    game.get_user_action = original_get_user_action

    return action


def start_game():
    """Text-based CLI interface for the poker game."""
    game = TexasHoldEmGame()
    game.start_game()

    playing = True
    while playing:
        # Display current game state
        display_table(game)

        if game.message:
            print(f"\n{game.message}")

        # If hand is complete, ask to play again
        if game.hand_complete:
            play_again = input("\nPlay another hand? (y/n): ")
            if play_again.lower() != "y":
                playing = False
            else:
                game.start_new_hand()
            continue

        # Handle user's turn
        user_action = handle_user_turn(game)

        # If user chose 'continue' and betting is complete, advance the game
        if user_action == "continue" and game.betting_round_complete:
            game.play_round()

    print("\nThanks for playing Texas Hold'em Poker!")
