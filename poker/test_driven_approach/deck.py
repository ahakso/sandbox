class Deck:
    def __init__(self):
        self.cards = [
            f"{value}{suit}"
            for suit in "SHDC"  # Spades, Hearts, Diamonds, Clubs
            for value in [
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "J",
                "Q",
                "K",
                "A",
            ]
        ]

    def shuffle(self):
        import random

        random.shuffle(self.cards)

    def deal(self, num_cards):
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards
