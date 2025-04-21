# Integration tests for Texas Hold'em game
import unittest
from unittest.mock import patch
import io
import sys
from contextlib import redirect_stdout
from game_logic import TexasHoldEmGame
from hand_evaluator import HandEvaluator


class TestGameIntegration(unittest.TestCase):
    """Integration tests for the Texas Hold'em game."""

    def setUp(self):
        """Set up for each test."""
        self.game = TexasHoldEmGame()

    @patch("builtins.print")  # Suppress output
    @patch("builtins.input")  # Mock input
    def test_complete_hand(self, mock_input, mock_print):
        """Test playing a complete hand."""
        # Configure the input mock to return appropriate values when called
        mock_input.side_effect = ["call", "check", "check", "check"]

        game = TexasHoldEmGame()
        game.start_new_hand()

        # Override the get_user_action method to use our mocked input
        original_get_user_action = game.get_user_action
        game.get_user_action = lambda: mock_input()

        # Pre-flop betting round
        game.collect_bets()
        game.betting_round_complete = True
        game.play_round()

        # Flop betting round
        game.collect_bets()
        game.betting_round_complete = True
        game.play_round()

        # Turn betting round
        game.collect_bets()
        game.betting_round_complete = True
        game.play_round()

        # River betting round
        game.collect_bets()
        game.betting_round_complete = True
            game.play_round()

        # Need one more play_round call to finish the game after river
        result = game.play_round()

        # Restore original method
        game.get_user_action = original_get_user_action

        # Verify the hand completed and a winner was determined
        assert result is True
        assert game.current_stage == "complete"
        assert game.last_winner is not None

    def test_hand_evaluation(self):
        """Test that hand evaluation works correctly across different hands."""
        test_cases = [
            # Royal flush
            {
                "hole": ["AS", "KS"],
                "community": ["QS", "JS", "TS", "2H", "3C"],
                "expected_rank": 9,
                "expected_desc": "Royal Flush",
            },
            # Straight flush
            {
                "hole": ["9S", "8S"],
                "community": ["7S", "6S", "5S", "KH", "AC"],
                "expected_rank": 8,
                "expected_desc": "Straight Flush",
            },
            # Four of a kind
            {
                "hole": ["AH", "AS"],
                "community": ["AD", "AC", "2S", "KH", "QC"],
                "expected_rank": 7,
                "expected_desc": "Four of a Kind",
            },
            # Full house
            {
                "hole": ["AH", "AS"],
                "community": ["AD", "KS", "KC", "2H", "QC"],
                "expected_rank": 6,
                "expected_desc": "Full House",
            },
            # Flush
            {
                "hole": ["AH", "3H"],
                "community": ["KH", "QH", "7H", "2S", "5C"],
                "expected_rank": 5,
                "expected_desc": "Flush",
            },
            # Straight
            {
                "hole": ["9S", "8H"],
                "community": ["7C", "6D", "5H", "KH", "AC"],
                "expected_rank": 4,
                "expected_desc": "Straight",
            },
            # Three of a kind
            {
                "hole": ["AH", "AS"],
                "community": ["AD", "3S", "5C", "KH", "QC"],
                "expected_rank": 3,
                "expected_desc": "Three of a Kind",
            },
            # Two pair
            {
                "hole": ["AH", "AS"],
                "community": ["KD", "KS", "5C", "2H", "QC"],
                "expected_rank": 2,
                "expected_desc": "Two Pair",
            },
            # One pair
            {
                "hole": ["AH", "KS"],
                "community": ["AD", "2S", "5C", "7H", "QC"],
                "expected_rank": 1,
                "expected_desc": "One Pair",
            },
            # High card
            {
                "hole": ["AH", "KS"],
                "community": ["QD", "JS", "9C", "7H", "3C"],
                "expected_rank": 0,
                "expected_desc": "High Card",
            },
        ]

        for i, test in enumerate(test_cases):
            with self.subTest(i=i, hand=test["expected_desc"]):
                result = HandEvaluator.evaluate_best_hand(test["hole"], test["community"])
                self.assertEqual(result["rank"], test["expected_rank"])
                self.assertIn(test["expected_desc"], result["description"])


if __name__ == "__main__":
    unittest.main()
