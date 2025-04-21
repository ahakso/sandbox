import pytest
from deck import Deck


def test_deck_initialization():
    deck = Deck()
    assert len(deck.cards) == 52
    assert "AS" in deck.cards  # Ace of Spades
    assert "10H" in deck.cards  # 10 of Hearts


def test_deck_shuffle():
    deck = Deck()
    original_order = deck.cards[:]
    deck.shuffle()
    assert deck.cards != original_order  # Ensure the deck is shuffled
    assert sorted(deck.cards) == sorted(original_order)  # Ensure no cards are lost


def test_deck_deal():
    deck = Deck()
    dealt_cards = deck.deal(5)
    assert len(dealt_cards) == 5
    assert len(deck.cards) == 47
    for card in dealt_cards:
        assert card not in deck.cards
