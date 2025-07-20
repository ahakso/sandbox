import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        return f"Card('{self.suit}', '{self.rank}')"

    def value(self):
        if self.rank.isdigit():
            return int(self.rank)
        elif self.rank == 'T':
            return 10
        elif self.rank == 'J':
            return 11
        elif self.rank == 'Q':
            return 12
        elif self.rank == 'K':
            return 13
        elif self.rank == 'A':
            return 14
        else:
            return 0  # Invalid rank


class Deck:
    def __init__(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            return None


class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.hand = []
        self.chips = chips
        self.bet = 0
        self.folded = False
        self.all_in = False

    def __str__(self):
        return f"{self.name} (Chips: {self.chips}, Hand: {self.hand})"

    def receive_card(self, card):
        self.hand.append(card)

    def clear_hand(self):
        self.hand = []

    def place_bet(self, amount):
        """Places a bet for the player.

        Args:
            amount (int): The desired amount to bet.

        Returns:
            int: The actual amount bet (capped at player's chip count).
        """
        if amount < 0:
            amount = 0 # Cannot bet negative amounts

        actual_bet = min(amount, self.chips) # Bet cannot exceed available chips
        self.chips -= actual_bet
        self.bet += actual_bet # Add to the total bet for this round
        self.all_in = (self.chips == 0 and actual_bet > 0) # Set all_in if chips are gone
        return actual_bet


class GameState:
    """Manages the state of a Texas Hold'em game."""

    def __init__(self, players, small_blind=10, big_blind=20):
        """Initializes the game state.

        Args:
            players (list): A list of Player objects participating in the game.
            small_blind (int): The amount of the small blind.
            big_blind (int): The amount of the big blind.
        """
        if not players or len(players) < 2:
            raise ValueError("Game requires at least two players.")

        self.players = players
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []
        self.small_blind_amount = small_blind
        self.big_blind_amount = big_blind
        self.dealer_button_pos = -1 # Start before the first player, will rotate to 0 on first hand
        self.current_player_index = -1 # Will be set when a betting round starts
        self.current_bet_level = 0 # The highest bet amount players need to match in the current round

    def rotate_button(self):
        """Moves the dealer button to the next active player."""
        # Simple rotation for now, doesn't account for players leaving/busting yet
        self.dealer_button_pos = (self.dealer_button_pos + 1) % len(self.players)
        print(f"Dealer button moved to Player {self.players[self.dealer_button_pos].name}")

    def add_to_pot(self, amount):
        """Adds chips to the main pot.

        Args:
            amount (int): The amount to add to the pot.
        """
        if amount > 0:
            self.pot += amount
            print(f"Added {amount} to pot. Pot is now {self.pot}")

    def post_blinds(self):
        """Posts the small and big blinds."""
        num_players = len(self.players)
        if num_players < 2:
            print("Not enough players to post blinds.")
            return

        # Determine blind positions relative to the button
        sb_pos = (self.dealer_button_pos + 1) % num_players
        bb_pos = (self.dealer_button_pos + 2) % num_players

        print(f"{self.players[sb_pos].name} posts small blind ({self.small_blind_amount})")
        sb_bet = self.players[sb_pos].place_bet(self.small_blind_amount)
        self.add_to_pot(sb_bet)

        print(f"{self.players[bb_pos].name} posts big blind ({self.big_blind_amount})")
        bb_bet = self.players[bb_pos].place_bet(self.big_blind_amount)
        self.add_to_pot(bb_bet)

        # The big blind sets the initial bet level for the pre-flop round
        self.current_bet_level = self.big_blind_amount

        # The player after the big blind starts the pre-flop action
        self.current_player_index = (bb_pos + 1) % num_players
        print(f"Action starts with {self.players[self.current_player_index].name}")

    def _burn_card(self):
        """Deals one card from the deck and discards it (burn card).
        Returns True if a card was successfully burned, False otherwise."""
        burned_card = self.deck.deal()
        if burned_card:
            print(f"Burned card: {burned_card}")
        else:
            # This should ideally not happen if pre-checks in calling methods are correct
            print("Warning: Could not burn card, deck might be empty or too short.")
        return burned_card is not None

    def deal_flop(self):
        """Deals the flop (3 community cards) after burning one card.
        Returns True on success, False on failure (e.g., insufficient cards)."""
        if len(self.deck.cards) < 4: # 1 burn + 3 flop cards
            print("Not enough cards in deck to deal flop.")
            return False

        if self._burn_card():
            flop_cards = [self.deck.deal() for _ in range(3)]
            if all(c is not None for c in flop_cards): # Ensure all 3 cards were dealt
                self.community_cards.extend(flop_cards)
                print(f"Flop dealt: {[str(c) for c in flop_cards]}")
                print(f"Current community cards: {[str(c) for c in self.community_cards]}")
                return True
            else:
                print("Error: Failed to deal all flop cards after burn.")
                # Note: Burned card is not returned to deck. Game state might be inconsistent for this deal.
                return False
        return False # Burn card failed

    def deal_turn(self):
        """Deals the turn (1 community card) after burning one card.
        Returns True on success, False on failure."""
        if len(self.deck.cards) < 2: # 1 burn + 1 turn card
            print("Not enough cards in deck to deal turn.")
            return False
        if self._burn_card():
            turn_card = self.deck.deal()
            if turn_card:
                self.community_cards.append(turn_card)
                print(f"Turn dealt: {turn_card}")
                print(f"Current community cards: {[str(c) for c in self.community_cards]}")
                return True
        return False

    def reset_player_bets_for_new_round(self):
        """Resets player bets for the start of a new betting street (e.g., after flop, before turn)."""
        for player in self.players:
            player.bet = 0  # Reset individual bets for the new street
        # self.current_bet_level is reset by start_betting_round for post-flop
        # or was set by post_blinds for pre-flop.

    def start_betting_round(self, is_preflop=False):
        """Manages a single betting round according to Texas Hold'em rules."""
        num_players = len(self.players)

        if not is_preflop:
            self.current_bet_level = 0 # Reset for new street (flop, turn, river)
            # Determine starting player (first active player left of button)
            # Ensure current_player_index is valid before starting loop
            found_starter = False
            potential_starter_idx = (self.dealer_button_pos + 1) % num_players
            for i in range(num_players):
                current_check_idx = (potential_starter_idx + i) % num_players
                p = self.players[current_check_idx]
                if not p.folded and p.chips > 0: # Must be able to initiate action
                    self.current_player_index = current_check_idx
                    found_starter = True
                    break
            if not found_starter:
                # This can happen if all remaining players are all-in already
                num_unfolded = sum(1 for p_obj in self.players if not p_obj.folded)
                if num_unfolded > 1 : # More than one player left, but all might be all-in
                    print("Betting round skipped: No player found who can initiate action (e.g., all remaining are all-in).")
                else: # Only one or zero players left
                    print("Betting round skipped: Not enough active players.")
                return
        # Preflop: self.current_player_index and self.current_bet_level are set by post_blinds()

        print(f"\n--- Starting Betting Round {'(Pre-flop)' if is_preflop else ''} ---")
        print(f"Pot: {self.pot}, Current Bet to Match: {self.current_bet_level}")
        if self.current_player_index != -1:
             print(f"Initial player to act: {self.players[self.current_player_index].name}")
        else: # Should be caught by logic above for post-flop
            print("Error: current_player_index not properly set before betting round.")
            return

        # Index of the player who made the last bet/raise.
        # If preflop, BB is the initial "aggressor" due to the blind.
        last_aggressor_idx = -1
        if is_preflop:
            last_aggressor_idx = (self.dealer_button_pos + 2) % num_players # BB index
        
        # Number of players who have acted since the last aggressive action.
        # Resets to 0 if a bet/raise occurs.
        actions_this_sequence = 0
        
        # Minimum number of players that need to act to potentially close the round.
        # This is the count of players who are not folded and not already all-in for the current bet or more.
        min_actors_needed = sum(1 for p in self.players if not p.folded and not (p.all_in and p.bet >= self.current_bet_level))


        while True:
            num_unfolded_players = sum(1 for p in self.players if not p.folded)
            if num_unfolded_players <= 1:
                print("Betting round ends: One or no players left.")
                break

            current_player_obj = self.players[self.current_player_index]

            # Skip player if folded or all-in and cannot act further
            # (i.e., already met current bet or is all-in for less but has no more chips)
            if current_player_obj.folded or \
               (current_player_obj.all_in and current_player_obj.chips == 0):
                
                # Check if skipping this player (who might be the last aggressor) closes the round
                if self.current_player_index == last_aggressor_idx and actions_this_sequence >= min_actors_needed -1 : # -1 because aggressor doesn't act against self
                    all_others_settled = True
                    for i, p_other in enumerate(self.players):
                        if i == self.current_player_index or p_other.folded or (p_other.all_in and p_other.chips == 0):
                            continue
                        if p_other.bet < self.current_bet_level: # Someone hasn't matched
                            all_others_settled = False; break
                    if all_others_settled:
                        print(f"Betting round ends: Action back to last aggressor ({current_player_obj.name}) who is already settled.")
                        break
                
                self.current_player_index = (self.current_player_index + 1) % num_players
                # actions_this_sequence +=1 # Incrementing for a skipped player is likely incorrect
                continue

            print(f"\nAction on {current_player_obj.name} (Chips: {current_player_obj.chips}, Round Bet: {current_player_obj.bet})")
            amount_to_call = self.current_bet_level - current_player_obj.bet
            print(f"Pot: {self.pot}, To Call: {max(0, amount_to_call)}")

            # Simulate getting player action
            action, new_total_bet_for_round = self.simulate_player_action(current_player_obj, amount_to_call, self.current_bet_level)
            
            made_aggressive_action_this_turn = False

            if action == "fold":
                current_player_obj.folded = True
                print(f"{current_player_obj.name} folds.")
            elif action == "check":
                if amount_to_call <= 0: # Can check
                    print(f"{current_player_obj.name} checks.")
                else: # Invalid action
                    print(f"Invalid action: {current_player_obj.name} cannot check. Must call {amount_to_call}. Auto-folding.")
                    current_player_obj.folded = True
            elif action == "call":
                if amount_to_call > 0:
                    bet_placed = current_player_obj.place_bet(amount_to_call)
                    self.add_to_pot(bet_placed)
                    print(f"{current_player_obj.name} calls {bet_placed}{' (All-in)' if current_player_obj.all_in else ''}.")
                elif amount_to_call == 0 : # Calling 0 is like checking
                     print(f"{current_player_obj.name} effectively checks (already met bet).")
                else: # Should not happen (calling negative)
                    print(f"Error: Invalid call amount for {current_player_obj.name}. Auto-folding.")
                    current_player_obj.folded = True
            elif action == "bet" or action == "raise":
                amount_player_adds = new_total_bet_for_round - current_player_obj.bet
                is_opening_bet = (self.current_bet_level == 0 and current_player_obj.bet == 0)

                # Basic Validation:
                # Bet/Raise amount must be valid (e.g. at least min bet/raise, or all-in)
                # Min bet is big blind. Min raise is usually the size of the last bet/raise increment.
                # For simplicity, min raise increment is big_blind_amount.
                valid_aggressive_action = False
                if is_opening_bet:
                    if new_total_bet_for_round >= self.big_blind_amount or current_player_obj.chips <= amount_player_adds: # Min bet or all-in
                        valid_aggressive_action = True
                else: # It's a raise
                    min_raise_to = self.current_bet_level + self.big_blind_amount # Simplified min raise
                    if new_total_bet_for_round >= min_raise_to or \
                       (current_player_obj.chips <= amount_player_adds and new_total_bet_for_round > self.current_bet_level): # Proper raise or valid all-in raise
                        valid_aggressive_action = True

                if valid_aggressive_action:
                    bet_placed = current_player_obj.place_bet(amount_player_adds)
                    self.add_to_pot(bet_placed)
                    print(f"{current_player_obj.name} {'bets' if is_opening_bet else 'raises to'} {current_player_obj.bet}{' (All-in)' if current_player_obj.all_in else ''}.")
                    
                    self.current_bet_level = current_player_obj.bet # New level to match
                    last_aggressor_idx = self.current_player_index
                    actions_this_sequence = 0 # Reset counter as action re-opens for others
                    min_actors_needed = sum(1 for p in self.players if not p.folded and not (p.all_in and p.bet >= self.current_bet_level))
                    made_aggressive_action_this_turn = True
                else:
                    print(f"Invalid {'bet' if is_opening_bet else 'raise'} by {current_player_obj.name} to {new_total_bet_for_round}. Auto-folding.")
                    current_player_obj.folded = True
            else: # Unknown action
                print(f"Unknown action '{action}' by {current_player_obj.name}. Auto-folding.")
                current_player_obj.folded = True

            actions_this_sequence += 1
            
            # Check for end of round conditions:
            # 1. Only one player left (handled at loop start).
            # 2. All active players have acted since the last bet/raise (actions_this_sequence >= min_actors_needed),
            #    AND all non-folded players have bets equal to current_bet_level (or are all-in for less).
            if actions_this_sequence >= min_actors_needed:
                all_bets_settled = True
                for p_check in self.players:
                    if not p_check.folded and not p_check.all_in and p_check.bet < self.current_bet_level:
                        all_bets_settled = False
                        break
                    if not p_check.folded and p_check.all_in and p_check.chips > 0 and p_check.bet < self.current_bet_level: # All-in with chips left but bet not covering
                        all_bets_settled = False # This case means they could have bet more if not all-in
                        break
                
                if all_bets_settled:
                    # Special pre-flop case: if BB was last_aggressor and action was only calls to BB, BB still has option.
                    is_bb_option_case = is_preflop and \
                                        last_aggressor_idx == (self.dealer_button_pos + 2) % num_players and \
                                        self.current_player_index == last_aggressor_idx and \
                                        not made_aggressive_action_this_turn and \
                                        self.current_bet_level == self.big_blind_amount
                    if not is_bb_option_case: # If it's not BB's option to re-open, round ends.
                        print(f"Betting round ends: All players acted in sequence and bets settled.")
                        break
                    else: # It is BB's option, they just checked/called. If they raised, made_aggressive_action_this_turn would be true.
                        print(f"BB ({current_player_obj.name}) had option and checked/called. Round ends.")
                        break 
            
            self.current_player_index = (self.current_player_index + 1) % num_players

        print("--- Betting Round Ended ---")
        print(f"Final Pot: {self.pot}")
        for p in self.players:
            if not p.folded:
                print(f"  {p.name}: Chips {p.chips}, Round Bet {p.bet}{' (All-in)' if p.all_in else ''}")
            else:
                print(f"  {p.name}: Folded")

    def simulate_player_action(self, player, amount_to_call, current_bet_level_on_table):
        """
        Simulates a player's action.
        Args:
            player (Player): The player object.
            amount_to_call (int): The amount player needs to add to their current bet to match.
            current_bet_level_on_table (int): The current highest total bet on the table for this round.
        Returns:
            tuple: (action_string, new_total_bet_for_round_int)
                   For "fold", "check", "call", new_total_bet_for_round_int is not strictly used by the caller for these actions
                   but represents the player's bet after the action (e.g. player.bet + amount_to_call for a call).
                   For "bet", "raise", new_total_bet_for_round_int is the new total bet player wants to make for this street.
        """
        # Simple AI:
        if amount_to_call == 0: # Can check
            # Chance to bet if checking is an option (opening bet)
            if current_bet_level_on_table == 0 and player.chips >= self.big_blind_amount and random.random() < 0.3: # 30% chance to bet
                bet_val = self.big_blind_amount # Bet big blind
                print(f"Sim AI: {player.name} BETS {bet_val}")
                return "bet", bet_val
            print(f"Sim AI: {player.name} CHECKS.")
            return "check", player.bet # Current bet doesn't change

        elif amount_to_call > 0 : # Must call, raise, or fold
            can_fully_call = player.chips >= amount_to_call
            
            # Chance to raise
            # Min raise would be to current_bet_level_on_table + (last raise amount, or BB if first raise)
            # Simplified: raise by at least big_blind_amount
            min_raise_total = current_bet_level_on_table + self.big_blind_amount
            if player.chips >= (min_raise_total - player.bet) and random.random() < 0.15 : # 15% chance to raise
                actual_raise_total = min_raise_total
                # Ensure player doesn't raise for more than they have (unless it's an all-in raise)
                if player.chips < (actual_raise_total - player.bet):
                    actual_raise_total = player.bet + player.chips # All-in raise
                
                print(f"Sim AI: {player.name} RAISES to {actual_raise_total}")
                return "raise", actual_raise_total

            # If not raising, decide to call or fold
            if can_fully_call:
                if random.random() < 0.85: # 85% chance to call
                    print(f"Sim AI: {player.name} CALLS {amount_to_call}")
                    return "call", current_bet_level_on_table # Target bet after call
                else:
                    print(f"Sim AI: {player.name} FOLDS instead of calling {amount_to_call}")
                    return "fold", player.bet
            elif player.chips > 0: # Must go all-in to call (partial call)
                print(f"Sim AI: {player.name} ALL-IN CALL for {player.chips}")
                return "call", player.bet + player.chips # Target bet after all-in call
            else: # No chips to even attempt a call
                print(f"Sim AI: {player.name} FOLDS (no chips to call).")
                return "fold", player.bet
        else: # Should not be reached if amount_to_call is negative
            print(f"Sim AI: {player.name} FOLDS (default/error state).")
            return "fold", player.bet

    def deal_river(self):
        """Deals the river (1 community card) after burning one card.
        Returns True on success, False on failure."""
        if len(self.deck.cards) < 2: # 1 burn + 1 river card
            print("Not enough cards in deck to deal river.")
            return False
        if self._burn_card():
            river_card = self.deck.deal()
            if river_card:
                self.community_cards.append(river_card)
                print(f"River dealt: {river_card}")
                print(f"Current community cards: {[str(c) for c in self.community_cards]}")
                return True
        return False