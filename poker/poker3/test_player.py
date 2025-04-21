import pytest
from player import Player


@pytest.fixture
def setup_player():
    return Player(name="Test Player", is_bot=True, chips=100)


def test_player_initialization():
    human = Player(name="Alice", is_bot=False)
    bot = Player(name="Bot1", is_bot=True)

    assert human.name == "Alice"
    assert not human.is_bot
    assert human.hand == []

    assert bot.name == "Bot1"
    assert bot.is_bot
    assert bot.hand == []


def test_player_receive_cards():
    player = Player(name="Alice")
    player.receive_cards(["AS", "KH"])
    assert player.hand == ["AS", "KH"]


def test_player_receive_invalid_cards():
    player = Player(name="Alice")
    with pytest.raises(ValueError, match="A player must receive exactly 2 cards."):
        player.receive_cards(["AS"])


def test_player_chips():
    player = Player(name="Alice", chips=100)
    assert player.chips == 100

    player.add_chips(50)
    assert player.chips == 150

    player.deduct_chips(30)
    assert player.chips == 120

    with pytest.raises(ValueError, match="Cannot add a negative amount of chips."):
        player.add_chips(-10)

    with pytest.raises(ValueError, match="Cannot deduct a negative amount of chips."):
        player.deduct_chips(-10)

    with pytest.raises(
        ValueError, match="Cannot deduct more chips than the player has."
    ):
        player.deduct_chips(200)


def test_take_action_call(setup_player):
    player = setup_player
    pot = 0
    action, pot = player.take_action(current_bet=50, pot=pot)
    assert action == "call"
    assert player.chips == 50
    assert pot == 50


def test_take_action_all_in(setup_player):
    player = setup_player
    player.chips = 30
    pot = 0
    action, pot = player.take_action(current_bet=50, pot=pot)
    assert action == "all-in"
    assert player.chips == 0
    assert pot == 30


def test_take_action_check(setup_player):
    player = setup_player
    player.chips = 0
    pot = 0
    action, pot = player.take_action(current_bet=50, pot=pot)
    assert action == "check"
    assert player.chips == 0
    assert pot == 0
