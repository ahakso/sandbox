class GameState:
    def __init__(self, players, dealer_index=0, small_blind=10):
        self.players = players
        self.dealer_index = dealer_index
        self.small_blind = small_blind
        self.pot = 0

    @property
    def big_blind(self):
        return self.small_blind * 2

    def get_player_chips(self):
        return {player.name: player.chips for player in self.players}

    def rotate_dealer(self):
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def get_dealer(self):
        return self.players[self.dealer_index]

    def get_blinds(self):
        return self.small_blind, self.big_blind

    def update_pot(self, amount):
        self.pot += amount

    def reset_pot(self):
        self.pot = 0
