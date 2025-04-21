import pytest
from game_state import GameState
from player import Player


@pytest.fixture
def setup_game_state():
    players = [
        Player(name="Player 1", chips=100),
        Player(name="Player 2", chips=200),
        Player(name="Player 3", chips=300),
    ]
    return GameState(players=players, dealer_index=0, small_blind=10)


def test_get_player_chips(setup_game_state):
    game_state = setup_game_state
    expected_chips = {
        "Player 1": 100,
        "Player 2": 200,
        "Player 3": 300,
    }
    assert game_state.get_player_chips() == expected_chips


def test_rotate_dealer(setup_game_state):
    game_state = setup_game_state
    assert game_state.get_dealer().name == "Player 1"
    game_state.rotate_dealer()
    assert game_state.get_dealer().name == "Player 2"
    game_state.rotate_dealer()
    assert game_state.get_dealer().name == "Player 3"
    game_state.rotate_dealer()
    assert game_state.get_dealer().name == "Player 1"


def test_get_blinds(setup_game_state):
    game_state = setup_game_state
    assert game_state.get_blinds() == (10, 20)


def test_update_and_reset_pot(setup_game_state):
    game_state = setup_game_state
    game_state.update_pot(50)
    assert game_state.pot == 50
    game_state.update_pot(30)
    assert game_state.pot == 80
    game_state.reset_pot()
    assert game_state.pot == 0
