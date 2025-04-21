# Core game logic for Texas Hold 'Em
import random
from hand_evaluator import HandEvaluator


class TexasHoldEmGame:
    def __init__(self):
        # Game setup
        self.players = ["User", "Bot1", "Bot2"]
        self.deck = []
        self.hands = {}
        self.community_cards = []
        self.chips = {player: 1000 for player in self.players}
        self.current_stage = None
        self.pot = 0
        self.current_bet = 0
        self.player_bets = {player: 0 for player in self.players}
        self.blinds = {"small": 10, "big": 20}

        # Game state flags
        self.betting_round_complete = False
        self.hand_complete = False
        self.last_winner = None
        self.dealer_position = 0

        # Game messages
        self.message = "Welcome to Texas Hold'Em!"

    def start_game(self):
        """Initialize a new game by starting a new hand."""
        self.start_new_hand()

    def start_new_hand(self):
        """Start a new hand of poker."""
        # Reset game state flags
        self.hand_complete = False
        self.betting_round_complete = False

        # Rotate dealer position to the next player
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

        # Initialize deck and shuffle
        self.deck = [f"{r}{s}" for r in "23456789TJQKA" for s in "CDHS"]
        random.shuffle(self.deck)

        # Initialize all players with cards
        self.hands = {}
        for i, player in enumerate(self.players):
            self.hands[player] = self.deck[i * 2 : i * 2 + 2]

        self.community_cards = []
        self.current_stage = "pre-flop"
        self.pot = 0
        self.current_bet = self.blinds["big"]
        self.player_bets = {player: 0 for player in self.players}

        # Post blinds
        small_blind_pos = (self.dealer_position + 1) % len(self.players)
        big_blind_pos = (self.dealer_position + 2) % len(self.players)
        self.chips[self.players[small_blind_pos]] -= self.blinds["small"]
        self.chips[self.players[big_blind_pos]] -= self.blinds["big"]
        self.player_bets[self.players[small_blind_pos]] = self.blinds["small"]
        self.player_bets[self.players[big_blind_pos]] = self.blinds["big"]
        self.pot = self.blinds["small"] + self.blinds["big"]

        self.message = "New hand started. Place your bets!"

    def process_game_state(self):
        """Main game state processor - returns true if UI should wait for user action."""
        # Check if we need to wait for user input for betting
        if not self.betting_round_complete and not self.hand_complete:
            # We're in a betting round, UI should handle collecting bets
            return True

        # If betting is complete, advance the game
        if self.betting_round_complete and not self.hand_complete:
            self.play_round()

            # After advancing, check if we need another betting round
            if self.current_stage == "complete":
                self.hand_complete = True
                return False
            else:
                # New stage started, need new betting round
                self.betting_round_complete = False
                return True

        # If hand is complete, nothing more to do
        return False

    def play_round(self):
        """Advance the game to the next stage."""
        # Check if only one player remains
        active_players = list(self.hands.keys())
        if len(active_players) <= 1:
            if active_players:
                # Award the pot to the last remaining player
                winner = active_players[0]
                self.last_winner = winner
                self.chips[winner] += self.pot
                self.message = f"{winner} wins ${self.pot} by default (all others folded)"
            else:
                self.message = "No active players remaining!"

            self.hand_complete = True
            self.current_stage = "complete"
            return True

        if self.betting_round_complete:
            # This is where we advance from one stage to the next
            self._advance_stage()

            # Reset betting variables for the new stage
            self.betting_round_complete = False
            self.current_bet = 0
            self.player_bets = {player: 0 for player in self.hands.keys()}

            # Set appropriate message for the new stage
            if self.current_stage == "flop":
                self.message = "Flop cards dealt. Place your bets!"
            elif self.current_stage == "turn":
                self.message = "Turn card dealt. Place your bets!"
            elif self.current_stage == "river":
                self.message = "River card dealt. Final betting round!"
            elif self.current_stage == "complete":
                self._determine_winner()
                self.hand_complete = True
                self.message = f"Hand complete! {self.last_winner} wins ${self.pot}"
                return True

        # Return False if hand is not complete
        return self.hand_complete

    def _advance_stage(self):
        """Advance to the next game stage."""
        stages = ["pre-flop", "flop", "turn", "river", "complete"]
        current_index = stages.index(self.current_stage)
        self.current_stage = stages[current_index + 1]

        if self.current_stage == "flop":
            self.community_cards.extend(self.deck[8:11])
        elif self.current_stage == "turn":
            self.community_cards.append(self.deck[11])
        elif self.current_stage == "river":
            self.community_cards.append(self.deck[12])

    def _determine_winner(self):
        """Determine the winner of the current hand."""
        active_players = list(self.hands.keys())

        # If only one player left, they win by default
        if len(active_players) == 1:
            winner = active_players[0]
            self.last_winner = winner
            self.chips[winner] += self.pot
            return winner

        best_hand = {"rank": -1, "high_card_values": []}
        winner = None

        for player, hand in self.hands.items():
            result = HandEvaluator.evaluate_best_hand(hand, self.community_cards)
            if result["rank"] > best_hand["rank"] or (
                result["rank"] == best_hand["rank"] and result["high_card_values"] > best_hand["high_card_values"]
            ):
                best_hand = result
                winner = player

        self.last_winner = winner
        self.chips[winner] += self.pot
        return winner

    def determine_winner(self):
        """Public interface for determining the winner (calls _determine_winner)"""
        return self._determine_winner()

    def collect_bets(self):
        """Collect bets from active players."""
        active_players = list(self.hands.keys())
        if not active_players:
            self.betting_round_complete = True
            return

        for player in list(self.hands.keys()):  # Create a copy of keys to avoid runtime modification issues
            # Skip players who are all-in (have no chips)
            if self.chips[player] <= 0:
                continue

            if player == "User":
                action = self.get_user_action()
            else:
                action = self._get_bot_action(player)

            self._process_action(player, action)

        # Check if all active players have matched the bet or folded
        active_players = list(self.hands.keys())
        if not active_players:
            self.betting_round_complete = True
        else:
            active_bets = {
                player: bet
                for player, bet in self.player_bets.items()
                if player in self.hands and self.chips[player] > 0
            }
            all_in_players = [player for player in self.hands if self.chips[player] <= 0]

            # If all active players are all-in or have matched the bet, complete the round
            if (not active_bets) or (all(bet == max(active_bets.values()) for bet in active_bets.values())):
                self.betting_round_complete = True
                self.message = f"Betting round complete. Click to continue."

    def _process_action(self, player, action):
        """Process a player's betting action."""
        if action == "fold":
            # Make sure the player is actually removed from hands
            if player in self.hands:
                del self.hands[player]
                self.message = f"{player} folds."
        elif action == "check":
            # Check is essentially doing nothing - player's bet stays the same
            self.message = f"{player} checks."
        elif action == "call":
            # Calculate how much more the player needs to add to match the current bet
            call_amount = min(self.chips[player], self.current_bet - self.player_bets[player])
            self.chips[player] -= call_amount
            self.player_bets[player] += call_amount
            self.pot += call_amount
            self.message = f"{player} calls ${call_amount}."
        elif action == "raise":
            # Calculate the raise amount (current bet + 20 or all remaining chips)
            raise_amount = min(self.chips[player], self.current_bet + 20)
            # Deduct chips already bet in this round
            additional_amount = raise_amount - self.player_bets[player]
            self.chips[player] -= additional_amount
            self.pot += additional_amount
            self.current_bet = self.player_bets[player] + additional_amount
            self.player_bets[player] = self.current_bet
            self.message = f"{player} raises to ${self.current_bet}."

    def get_user_action(self):
        """Get action from user input - to be overridden by UI."""
        valid_actions = ["fold", "call", "check", "raise"]
        while True:
            action = input(f"Your action ({', '.join(valid_actions)}): ").lower()
            if action in valid_actions:
                return action

    def _get_bot_action(self, bot):
        """Simple bot logic for demo."""
        from random import random

        hand_strength = self._evaluate_bot_hand_strength(bot)

        # Adjust probabilities based on hand strength (0-1 scale)
        fold_prob = max(0, 0.4 - hand_strength * 0.5)  # Less likely to fold with good hands
        raise_prob = min(0.8, hand_strength * 0.7)  # More likely to raise with good hands

        # Fold if hand is weak or randomly
        if random() < fold_prob:
            return "fold"
        # Raise if hand is strong or randomly
        elif random() < raise_prob:
            return "raise"
        # Otherwise call/check
        else:
            return "call"

    def _evaluate_bot_hand_strength(self, bot):
        """Simple hand strength evaluation for bots - returns value from 0-1."""
        # If no community cards yet, just evaluate hole cards
        if len(self.community_cards) == 0:
            # Check for pairs in hole cards
            if self.hands[bot][0][0] == self.hands[bot][1][0]:
                return 0.8  # High value for a pocket pair

            # Check for high cards
            high_cards = "AKQJT"
            if self.hands[bot][0][0] in high_cards and self.hands[bot][1][0] in high_cards:
                return 0.7  # High value for two high cards
            elif self.hands[bot][0][0] in high_cards or self.hands[bot][1][0] in high_cards:
                return 0.5  # Medium value for one high card

            return 0.3  # Low value for no high cards or pairs

        # With community cards, use the hand evaluator
        result = HandEvaluator.evaluate_best_hand(self.hands[bot], self.community_cards)

        # Scale the rank to 0-1
        return min(1.0, result["rank"] / 8.0)

    def get_valid_actions(self):
        """Return the list of valid actions for the current user."""
        if "User" not in self.hands or self.hand_complete:
            # If user has folded or hand is complete, only continue is valid
            return ["continue"]

        if not self.betting_round_complete:
            # Basic actions
            valid_actions = ["fold"]

            # Check if we can check or need to call
            if self.current_bet == 0 or self.current_bet == self.player_bets.get("User", 0):
                valid_actions.append("check")
            else:
                valid_actions.append("call")

            # Allow raise if player has chips
            if self.chips.get("User", 0) > 0:
                valid_actions.append("raise")

            return valid_actions
        else:
            # Between betting rounds, can only continue
            return ["continue"]
