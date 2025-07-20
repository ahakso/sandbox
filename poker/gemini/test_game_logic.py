import unittest
import sys
import os

# Add the directory containing game_logic.py to the Python path
# This allows importing the module even if the test is run from a different directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # Adjust if game_logic.py is elsewhere
sys.path.insert(0, parent_dir) # Or use the specific path to game_logic.py's directory

# Now import the classes
try:
    from gemini.game_logic import Card, Deck, Player, GameState
except ImportError:
    print("Error: Could not import Card, Deck, Player from gemini.game_logic.")
    print(f"Current sys.path: {sys.path}")
    # If the above path logic is wrong, you might need to adjust it based on your project structure
    # For example, if game_logic.py is in the same directory as the test file:
    # from game_logic import Card, Deck, Player
    raise # Re-raise the error if import fails


class TestCard(unittest.TestCase):

    def test_card_creation(self):
        card = Card("Hearts", "A")
        self.assertEqual(card.suit, "Hearts")
        self.assertEqual(card.rank, "A")

    def test_card_str(self):
        card = Card("Diamonds", "K")
        self.assertEqual(str(card), "K of Diamonds")

    def test_card_repr(self):
        card = Card("Spades", "10")
        # Note: Your current implementation uses 'T' for 10 in Deck,
        # but Card init takes the full rank string.
        # The repr reflects the arguments passed to __init__.
        # If you intended Card('Spades', 'T'), the repr would be different.
        # Let's assume the Deck uses 'T' but Card can be created with '10' or 'T'.
        # We'll test with 'T' as that's used in Deck.
        card_t = Card("Spades", "T")
        self.assertEqual(repr(card_t), "Card('Spades', 'T')")

    def test_card_value(self):
        self.assertEqual(Card("Clubs", "2").value(), 2)
        self.assertEqual(Card("Diamonds", "9").value(), 9)
        self.assertEqual(Card("Hearts", "T").value(), 10)
        self.assertEqual(Card("Spades", "J").value(), 11)
        self.assertEqual(Card("Clubs", "Q").value(), 12)
        self.assertEqual(Card("Diamonds", "K").value(), 13)
        self.assertEqual(Card("Hearts", "A").value(), 14)
        # Test invalid rank if needed, though Deck prevents this
        # self.assertEqual(Card("Hearts", "X").value(), 0)


class TestDeck(unittest.TestCase):

    def test_deck_creation(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        # Check for uniqueness (optional but good)
        unique_cards = set(str(card) for card in deck.cards)
        self.assertEqual(len(unique_cards), 52)

    def test_deck_shuffle(self):
        deck1 = Deck()
        deck2 = Deck()
        # Convert to string representations for comparison
        cards_before = [str(card) for card in deck1.cards]
        deck2.shuffle()
        cards_after = [str(card) for card in deck2.cards]

        # It's highly improbable they remain identical after shuffle
        self.assertNotEqual(cards_before, cards_after)
        # Ensure all original cards are still present
        self.assertCountEqual(cards_before, cards_after) # Checks elements regardless of order
        self.assertEqual(len(deck2.cards), 52)

    def test_deck_deal(self):
        deck = Deck()
        deck.shuffle() # Usually deal from a shuffled deck
        initial_len = len(deck.cards)

        card1 = deck.deal()
        self.assertIsInstance(card1, Card)
        self.assertEqual(len(deck.cards), initial_len - 1)

        # Deal all cards
        for _ in range(initial_len - 1):
            card = deck.deal()
            self.assertIsNotNone(card)

        self.assertEqual(len(deck.cards), 0)
        # Test dealing from empty deck
        empty_deal = deck.deal()
        self.assertIsNone(empty_deal)


class TestPlayer(unittest.TestCase):

    def test_player_creation(self):
        player = Player("Alice", 500)
        self.assertEqual(player.name, "Alice")
        self.assertEqual(player.chips, 500)
        self.assertEqual(player.hand, [])
        self.assertEqual(player.bet, 0)
        self.assertFalse(player.folded)
        self.assertFalse(player.all_in)

    def test_receive_card(self):
        player = Player("Bob")
        card = Card("Hearts", "7")
        player.receive_card(card)
        self.assertEqual(len(player.hand), 1)
        self.assertIn(card, player.hand)
        card2 = Card("Spades", "K")
        player.receive_card(card2)
        self.assertEqual(len(player.hand), 2)
        self.assertIn(card2, player.hand)

    def test_clear_hand(self):
        player = Player("Charlie")
        player.receive_card(Card("Diamonds", "Q"))
        player.clear_hand()
        self.assertEqual(player.hand, [])

    def test_place_bet_logic(self):
        # Note: The current place_bet only adjusts the amount variable
        # if it exceeds chips. It doesn't update player.bet or player.chips.
        # This test reflects the *current* logic.
        player = Player("Dave", 100)

        # Test betting less than stack
        bet_amount_normal = 50
        # The function currently doesn't return or modify state directly
        # We can't easily test the internal 'amount' variable adjustment directly
        # without modifying the function or testing side effects (which don't exist yet).
        # If the function were:
        # def place_bet(self, amount):
        #     actual_bet = min(amount, self.chips)
        #     self.bet += actual_bet
        #     self.chips -= actual_bet
        #     self.all_in = self.chips == 0
        # Then we could test:
        # player.place_bet(50)
        # self.assertEqual(player.bet, 50)
        # self.assertEqual(player.chips, 50)
        # self.assertFalse(player.all_in)

        # Test betting more than stack (all-in scenario based on current logic)
        bet_amount_all_in = 150
        # Again, we can't directly test the adjusted 'amount' variable easily.
        # If the function were implemented as above:
        # player.place_bet(150) # After resetting player state
        # self.assertEqual(player.bet, 100)
        # self.assertEqual(player.chips, 0)
        # self.assertTrue(player.all_in)
        pass # Placeholder as the current function has limited testable effects

class TestGameState(unittest.TestCase):

    def setUp(self):
        """Set up a common game state for tests."""
        self.player1 = Player("Alice", 1000)
        self.player2 = Player("Bob", 1000)
        self.player3 = Player("Charlie", 1000)
        self.players = [self.player1, self.player2, self.player3]
        self.game_state = GameState(self.players, small_blind=10, big_blind=20)
        # Note: setUp does not deal player cards or start a hand beyond GameState init.
        # The deck is full (52 cards) at the start of each test method here.
        # If tests require blinds posted, they should call:
        # self.game_state.rotate_button()
        # self.game_state.post_blinds()

    def test_deal_flop(self):
        initial_deck_size = len(self.game_state.deck.cards)
        self.assertTrue(self.game_state.deal_flop(), "Deal flop should succeed")
        self.assertEqual(len(self.game_state.community_cards), 3)
        for card in self.game_state.community_cards:
            self.assertIsInstance(card, Card)
        self.assertEqual(len(self.game_state.deck.cards), initial_deck_size - 4, "Deck size after flop") # 3 flop + 1 burn

    def test_deal_turn(self):
        self.assertTrue(self.game_state.deal_flop(), "Pre-condition: Flop must be dealt")
        initial_deck_size_after_flop = len(self.game_state.deck.cards)
        self.assertEqual(len(self.game_state.community_cards), 3)

        self.assertTrue(self.game_state.deal_turn(), "Deal turn should succeed")
        self.assertEqual(len(self.game_state.community_cards), 4, "Community cards after turn") # 3 flop + 1 turn
        self.assertIsInstance(self.game_state.community_cards[-1], Card)
        self.assertEqual(len(self.game_state.deck.cards), initial_deck_size_after_flop - 2, "Deck size after turn") # 1 turn + 1 burn

    def test_deal_river(self):
        self.assertTrue(self.game_state.deal_flop(), "Pre-condition: Flop must be dealt")
        self.assertTrue(self.game_state.deal_turn(), "Pre-condition: Turn must be dealt")
        initial_deck_size_after_turn = len(self.game_state.deck.cards)
        self.assertEqual(len(self.game_state.community_cards), 4)

        self.assertTrue(self.game_state.deal_river(), "Deal river should succeed")
        self.assertEqual(len(self.game_state.community_cards), 5, "Community cards after river") # 3 flop + 1 turn + 1 river
        self.assertIsInstance(self.game_state.community_cards[-1], Card)
        self.assertEqual(len(self.game_state.deck.cards), initial_deck_size_after_turn - 2, "Deck size after river") # 1 river + 1 burn

    def test_deal_sequence_community_cards(self):
        initial_deck_size = len(self.game_state.deck.cards) # Should be 52

        # Flop
        self.assertTrue(self.game_state.deal_flop())
        self.assertEqual(len(self.game_state.community_cards), 3)
        self.assertEqual(len(self.game_state.deck.cards), initial_deck_size - 4) # 52 - 4 = 48

        # Turn
        self.assertTrue(self.game_state.deal_turn())
        self.assertEqual(len(self.game_state.community_cards), 4)
        self.assertEqual(len(self.game_state.deck.cards), initial_deck_size - 4 - 2) # 48 - 2 = 46

        # River
        self.assertTrue(self.game_state.deal_river())
        self.assertEqual(len(self.game_state.community_cards), 5)
        self.assertEqual(len(self.game_state.deck.cards), initial_deck_size - 4 - 2 - 2) # 46 - 2 = 44

        # Ensure all community cards are unique Card instances
        community_card_reprs = {repr(card) for card in self.game_state.community_cards}
        self.assertEqual(len(community_card_reprs), 5, "Community cards should be unique")
        for card in self.game_state.community_cards:
            self.assertIsInstance(card, Card)

    def test_deal_flop_insufficient_cards(self):
        # Empty the deck to leave only 3 cards (needs 4 for flop + burn)
        for _ in range(len(self.game_state.deck.cards) - 3):
            self.game_state.deck.deal()
        self.assertEqual(len(self.game_state.deck.cards), 3)
        self.assertFalse(self.game_state.deal_flop(), "Flop deal should fail with insufficient cards")
        self.assertEqual(len(self.game_state.community_cards), 0)

    def test_deal_turn_insufficient_cards(self):
        self.assertTrue(self.game_state.deal_flop()) # Uses 4 cards, 48 left
        # Empty the deck to leave only 1 card (needs 2 for turn + burn)
        for _ in range(len(self.game_state.deck.cards) - 1):
            self.game_state.deck.deal()
        self.assertEqual(len(self.game_state.deck.cards), 1)
        self.assertFalse(self.game_state.deal_turn(), "Turn deal should fail with insufficient cards")
        self.assertEqual(len(self.game_state.community_cards), 3, "Flop cards should remain")

    def test_deal_river_insufficient_cards(self):
        self.assertTrue(self.game_state.deal_flop()) # Uses 4 cards
        self.assertTrue(self.game_state.deal_turn()) # Uses 2 cards (total 6 used)
        # Empty the deck to leave only 1 card (needs 2 for river + burn)
        for _ in range(len(self.game_state.deck.cards) - 1):
            self.game_state.deck.deal()
        self.assertEqual(len(self.game_state.deck.cards), 1)
        self.assertFalse(self.game_state.deal_river(), "River deal should fail with insufficient cards")
        self.assertEqual(len(self.game_state.community_cards), 4, "Flop and Turn cards should remain")

    # --- Betting Round Tests ---
    def _set_mock_actions(self, actions):
        """
        Sets up a sequence of actions to be returned by the mock.
        Args:
            actions (list): A list of tuples: 
                            (expected_player_name_str, 
                             (action_str, new_total_bet_value_for_round))
                            
                            new_total_bet_value_for_round:
                              - For "fold", "check": This value is largely for test documentation;
                                the mock will return player.bet as the second tuple element.
                              - For "call": The player's target total bet for the round 
                                (i.e., current_bet_level or their all-in amount if less).
                              - For "bet", "raise": The player's new total bet amount for the round.
        """
        self.mock_action_queue = actions # Store the whole list for the current test

        def mock_player_action_method(player, amount_to_call, current_bet_level_on_table):
            if not hasattr(self, 'mock_action_queue') or not self.mock_action_queue:
                # This case should ideally be avoided by providing sufficient actions in the test.
                # If reached, it means the game logic requested an action when the test didn't provide one.
                print(f"MOCK_ACTION: Queue empty or not set. Player {player.name} (to call {amount_to_call}) defaults to fold.")
                return "fold", player.bet 

            expected_player_name, (action_str, new_total_bet_val_from_queue) = self.mock_action_queue.pop(0)
            
            self.assertEqual(player.name, expected_player_name,
                             f"MOCK_ACTION: Expected {expected_player_name} to act (to call {amount_to_call}, current street bet {player.bet}), but it's {player.name}'s turn.")
            
            # This print helps trace test execution against the game's print statements.
            print(f"MOCK_ACTION: Player {player.name} (chips {player.chips}, current round bet {player.bet}, needs to call {amount_to_call} to meet {current_bet_level_on_table}) "
                  f"-> Test provides: {action_str} to total street bet of {new_total_bet_val_from_queue}")

            if action_str in ["fold", "check"]:
                # For fold/check, the second element returned by simulate_player_action
                # should be the player's current bet for the round (it doesn't change).
                return action_str, player.bet
            
            # For "call", "bet", "raise", the new_total_bet_val_from_queue is the
            # intended total bet of the player for the current betting round.
            # This is what the original simulate_player_action's second return value represents.
            return action_str, new_total_bet_val_from_queue
        
        # Replace the original simulate_player_action with our mock for this test
        self.game_state.simulate_player_action = mock_player_action_method

    def test_betting_round_preflop_folds_to_bb(self):
        # P1=Alice (D), P2=Bob (SB), P3=Charlie (BB). SB=10, BB=20.
        # P1 (UTG for 3 players) acts first.
        self.game_state.rotate_button() # P1/Alice is button (idx 0)
        self.game_state.post_blinds()   # P2/Bob SB=10, P3/Charlie BB=20. Pot=30. current_bet_level=20. P1/Alice (idx 0) to act.

        self.assertEqual(self.game_state.current_player_index, 0) # Alice to act
        self.assertEqual(self.player1.bet, 0)  # Alice's bet
        self.assertEqual(self.player2.bet, 10) # Bob's SB
        self.assertEqual(self.player3.bet, 20) # Charlie's BB

        # Action sequence: (player_name, action_string, new_total_bet_for_round)
        self._set_mock_actions([
            ("Alice", ("fold", 0)),    # Alice folds. Her bet for round remains 0.
            ("Bob", ("fold", 10)),     # Bob folds. His bet for round remains 10 (the SB).
            # Charlie (BB) wins by default. No action needed from Charlie.
        ])
        
        self.game_state.start_betting_round(is_preflop=True)

        self.assertTrue(self.player1.folded)
        self.assertTrue(self.player2.folded)
        self.assertFalse(self.player3.folded) # Charlie wins

        self.assertEqual(self.game_state.pot, 30) # Blinds are in the pot
        self.assertEqual(self.player1.chips, 1000) # Alice didn't bet beyond this
        self.assertEqual(self.player2.chips, 990)  # Bob lost SB
        self.assertEqual(self.player3.chips, 980)  # Charlie posted BB

        # Bets at end of round (for this street)
        self.assertEqual(self.player1.bet, 0)
        self.assertEqual(self.player2.bet, 10) 
        self.assertEqual(self.player3.bet, 20)

    def test_betting_round_preflop_sb_calls_bb_checks(self):
        # P1=Alice (D), P2=Bob (SB), P3=Charlie (BB). SB=10, BB=20.
        self.game_state.rotate_button() # Alice is button
        self.game_state.post_blinds()   # Bob SB=10, Charlie BB=20. Pot=30. Bet=20. Alice to act.

        self._set_mock_actions([
            ("Alice", ("fold", 0)),       # Alice folds.
            ("Bob", ("call", 20)),        # Bob (SB) calls the BB. His total bet becomes 20.
            ("Charlie", ("check", 20)),   # Charlie (BB) checks. His total bet remains 20.
        ])

        self.game_state.start_betting_round(is_preflop=True)

        self.assertTrue(self.player1.folded)
        self.assertFalse(self.player2.folded)
        self.assertFalse(self.player3.folded)

        self.assertEqual(self.game_state.pot, 40) # SB (10+10) + BB (20) = 40. Wait, Alice folds. SB calls BB. Pot = 10(SB)+10(SB call)+20(BB)=40
                                                # Initial pot = 30 (SB 10 + BB 20). Alice folds. Bob calls 10 more. Pot = 30 + 10 = 40.
        self.assertEqual(self.player1.chips, 1000)
        self.assertEqual(self.player2.chips, 980)  # Bob: 1000 - 10(SB) - 10(call) = 980
        self.assertEqual(self.player3.chips, 980)  # Charlie: 1000 - 20(BB) = 980

        self.assertEqual(self.player1.bet, 0)
        self.assertEqual(self.player2.bet, 20) # Bob's total bet for the round
        self.assertEqual(self.player3.bet, 20) # Charlie's total bet for the round

    def test_betting_round_preflop_utg_bets_all_fold(self):
        # P1=Alice (D, UTG), P2=Bob (SB), P3=Charlie (BB). SB=10, BB=20.
        self.game_state.rotate_button()
        self.game_state.post_blinds() # Pot=30. Bet=20. Alice to act.

        self._set_mock_actions([
            ("Alice", ("bet", 60)),      # Alice bets 60 (new total bet for round).
            ("Bob", ("fold", 10)),       # Bob (SB) folds. His bet remains 10.
            ("Charlie", ("fold", 20)),  # Charlie (BB) folds. His bet remains 20.
        ])

        self.game_state.start_betting_round(is_preflop=True)

        self.assertFalse(self.player1.folded) # Alice wins
        self.assertTrue(self.player2.folded)
        self.assertTrue(self.player3.folded)

        # Pot = 30 (blinds) + 60 (Alice's bet) = 90.
        # No, Alice's bet of 60 replaces the need to call 20.
        # Pot = SB (10) + BB (20) + Alice's raise amount (60). Total = 90.
        self.assertEqual(self.game_state.pot, 10 + 20 + 60) # SB + BB + Alice's bet
        self.assertEqual(self.player1.chips, 1000 - 60) # Alice
        self.assertEqual(self.player2.chips, 990)     # Bob
        self.assertEqual(self.player3.chips, 980)     # Charlie

        self.assertEqual(self.player1.bet, 60)
        self.assertEqual(self.player2.bet, 10)
        self.assertEqual(self.player3.bet, 20)

    def test_betting_round_postflop_check_bet_call(self):
        # P1=Alice (D), P2=Bob (SB), P3=Charlie (BB).
        # Assume preflop happened, bets were reset.
        self.game_state.rotate_button() # P1/Alice is button (idx 0)

        # Simulate a preflop state:
        # Alice (P1) folds. Bob (P2, SB) calls BB. Charlie (P3, BB) checks.
        # Initial chips: 1000 each.
        # For this scenario, P1 is Dealer. P2 is SB, P3 is BB.
        # If P1 folds, P2 (SB) needs to act on BB's 20. If P2 calls, P2's bet is 20. P3 (BB) can check.
        # P1 (Alice) - no bet, chips 1000, folded.
        # P2 (Bob) - SB 10, calls 10. Total preflop bet 20. Chips 1000 - 20 = 980.
        # P3 (Charlie) - BB 20. Total preflop bet 20. Chips 1000 - 20 = 980.
        # Pot = 40.
        self.player1.folded = True
        # self.player1.chips remains 1000

        self.player2.chips = 980 # Chips for P2 after simulated preflop
        # P2's preflop bet would have been 20, will be reset by reset_player_bets_for_new_round
        
        self.player3.chips = 980 # Chips for P3 after simulated preflop
        # P3's preflop bet would have been 20, will be reset

        self.game_state.pot = 40 # Pot carried from preflop

        self.game_state.reset_player_bets_for_new_round() # Bets for new street are 0
        self.game_state.current_player_index = 1 # Bob (P2, first active player left of button) to act post-flop
        
        # Assert initial conditions for THIS post-flop round
        self.assertEqual(self.player2.chips, 980, "P2 initial chips for post-flop round")
        self.assertEqual(self.player3.chips, 980, "P3 initial chips for post-flop round")
        self.assertEqual(self.player2.bet, 0, "P2 bet for new street before it starts")
        self.assertEqual(self.player3.bet, 0, "P3 bet for new street before it starts")
        self.assertEqual(self.game_state.current_bet_level, 0) # Post-flop starts with 0 bet level

        self._set_mock_actions([
            ("Bob", ("check", 0)),      # Bob checks. His bet for street remains 0.
            ("Charlie", ("bet", 50)),   # Charlie bets 50. His bet for street becomes 50.
            ("Bob", ("call", 50)),      # Bob calls Charlie's 50. His bet for street becomes 50.
        ])

        self.game_state.start_betting_round(is_preflop=False)

        # Assert final state AFTER the betting round
        self.assertTrue(self.player1.folded)
        self.assertFalse(self.player2.folded)
        self.assertFalse(self.player3.folded)

        # Pot: 40 (preflop) + 50 (Charlie's bet) + 50 (Bob's call) = 140
        self.assertEqual(self.game_state.pot, 140)
        
        # Chips:
        # P2 (Bob): 980 (start of round) - 50 (call) = 930
        # P3 (Charlie): 980 (start of round) - 50 (bet) = 930
        self.assertEqual(self.player2.chips, 930, "P2 final chips")
        self.assertEqual(self.player3.chips, 930, "P3 final chips")

        self.assertEqual(self.player2.bet, 50) # Bob's bet for this street
        self.assertEqual(self.player3.bet, 50) # Charlie's bet for this street


if __name__ == '__main__':
    unittest.main()