import pytest
from deck import Deck
from player import Player
from round import Round


@pytest.fixture
def setup_round():
    deck = Deck()
    players = [Player("Player 1"), Player("Player 2")]
    return Round(players, deck)


def test_pre_flop(setup_round):
    round_instance = setup_round
    round_instance.pre_flop()
    for player in round_instance.players:
        assert len(player.hand) == 2


def test_flop(setup_round):
    round_instance = setup_round
    round_instance.flop()
    assert len(round_instance.community_cards) == 3


def test_turn(setup_round):
    round_instance = setup_round
    round_instance.turn()
    assert len(round_instance.community_cards) == 1


def test_river(setup_round):
    round_instance = setup_round
    round_instance.river()
    assert len(round_instance.community_cards) == 1


def test_play_round(setup_round):
    round_instance = setup_round
    round_instance.play_round()
    assert len(round_instance.community_cards) == 5
    for player in round_instance.players:
        assert len(player.hand) == 2
