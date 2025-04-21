# Bot behavior for Texas Hold 'Em
import random


class Bot:
    def __init__(self, name, style="balanced"):
        self.name = name
        self.style = style  # balanced, aggressive, conservative
        self.hand = []

    def decide_action(self, valid_actions, current_bet=0, pot_size=0, community_cards=None):
        """Decide bot's action based on current game state."""
        if not community_cards:
            community_cards = []

        # Simple decision making based on style
        if self.style == "aggressive":
            return "raise" if "raise" in valid_actions else "call"
        elif self.style == "conservative":
            return "fold" if current_bet > 0 else "check"

        # Balanced style - default
        if "check" in valid_actions:
            return "check"
        elif "call" in valid_actions:
            return "call"
        return "fold"
