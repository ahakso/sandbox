class Player:
    def __init__(self, name, is_bot=False, chips=0):
        self.name = name
        self.is_bot = is_bot
        self.hand = []
        self.chips = chips

    def receive_cards(self, cards):
        if len(cards) != 2:
            raise ValueError("A player must receive exactly 2 cards.")
        self.hand = cards

    def show_hand(self):
        return self.hand

    def add_chips(self, amount):
        if amount < 0:
            raise ValueError("Cannot add a negative amount of chips.")
        self.chips += amount

    def deduct_chips(self, amount):
        if amount < 0:
            raise ValueError("Cannot deduct a negative amount of chips.")
        if amount > self.chips:
            raise ValueError("Cannot deduct more chips than the player has.")
        self.chips -= amount

    def take_action(self, current_bet, pot):
        if self.chips >= current_bet:
            self.chips -= current_bet
            pot += current_bet
            return "call", pot
        elif self.chips > 0:
            pot += self.chips
            self.chips = 0
            return "all-in", pot
        return "check", pot
