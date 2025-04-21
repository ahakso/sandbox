class Round:
    def __init__(self, players, deck):
        self.players = players
        self.deck = deck
        self.community_cards = []
        self.pot = 0

    def pre_flop(self):
        for player in self.players:
            player.receive_cards(self.deck.deal(2))

    def betting_stage(self):
        for player in self.players:
            # Placeholder for player actions: check, call, raise
            pass

    def flop(self):
        self.community_cards.extend(self.deck.deal(3))

    def turn(self):
        self.community_cards.extend(self.deck.deal(1))

    def river(self):
        self.community_cards.extend(self.deck.deal(1))

    def play_round(self):
        self.pre_flop()
        self.betting_stage()
        self.flop()
        self.betting_stage()
        self.turn()
        self.betting_stage()
        self.river()
        self.betting_stage()
