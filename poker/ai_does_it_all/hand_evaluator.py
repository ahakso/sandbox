# Hand evaluation logic for Texas Hold'em
class HandEvaluator:
    @staticmethod
    def evaluate_best_hand(hole_cards, community_cards):
        """Evaluate the best possible hand from hole cards and community cards."""
        all_cards = hole_cards + community_cards
        rank_values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        # Extract ranks and suits
        ranks = [card[0] for card in all_cards]
        suits = [card[1] for card in all_cards]
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}

        # Check for flush
        flush_suit = next((suit for suit in set(suits) if suits.count(suit) >= 5), None)
        flush_cards = [card for card in all_cards if card[1] == flush_suit] if flush_suit else []

        # Check for straight
        values = sorted([rank_values[r] for r in ranks])
        straight_high = None
        for i in range(len(values) - 4):
            if values[i : i + 5] == list(range(values[i], values[i] + 5)):
                straight_high = values[i + 4]

        # Special case: Ace-low straight (A,2,3,4,5)
        if set([14, 2, 3, 4, 5]).issubset(values):
            straight_high = 5

        # Check for straight flush (if we have a flush)
        straight_flush_high = None
        if flush_suit:
            # Get sorted values of flush cards
            flush_values = sorted([rank_values[card[0]] for card in flush_cards])
            # Check for regular straights within the flush cards
            for i in range(len(flush_values) - 4):
                if flush_values[i : i + 5] == list(range(flush_values[i], flush_values[i] + 5)):
                    straight_flush_high = flush_values[i + 4]
            # Check for A-5 straight flush
            if set([14, 2, 3, 4, 5]).issubset(flush_values):
                straight_flush_high = 5

        # Evaluate hand
        # Royal Flush
        if flush_suit and straight_flush_high == 14:
            return {"rank": 9, "description": "Royal Flush", "high_card_values": [14]}

        # Straight Flush
        if straight_flush_high:
            return {"rank": 8, "description": f"Straight Flush", "high_card_values": [straight_flush_high]}

        # Four of a Kind
        if 4 in rank_counts.values():
            rank = next(r for r, count in rank_counts.items() if count == 4)
            return {"rank": 7, "description": f"Four of a Kind", "high_card_values": [rank_values[rank]]}

        # Full House
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            three_rank = next(r for r, count in rank_counts.items() if count == 3)
            two_rank = next(r for r, count in rank_counts.items() if count == 2)
            return {
                "rank": 6,
                "description": f"Full House",
                "high_card_values": [rank_values[three_rank], rank_values[two_rank]],
            }

        # Flush
        if flush_suit:
            flush_values = sorted([rank_values[card[0]] for card in flush_cards], reverse=True)
            return {"rank": 5, "description": f"Flush", "high_card_values": flush_values[:5]}

        # Straight
        if straight_high:
            return {"rank": 4, "description": f"Straight", "high_card_values": [straight_high]}

        # Three of a Kind
        if 3 in rank_counts.values():
            rank = next(r for r, count in rank_counts.items() if count == 3)
            return {"rank": 3, "description": f"Three of a Kind", "high_card_values": [rank_values[rank]]}

        # Two Pair
        pairs = [r for r, count in rank_counts.items() if count == 2]
        if len(pairs) >= 2:
            pair_values = sorted([rank_values[p] for p in pairs], reverse=True)
            return {"rank": 2, "description": f"Two Pair", "high_card_values": pair_values[:2]}

        # One Pair
        if 2 in rank_counts.values():
            rank = next(r for r, count in rank_counts.items() if count == 2)
            return {"rank": 1, "description": f"One Pair", "high_card_values": [rank_values[rank]]}

        # High Card
        high_values = sorted([rank_values[r] for r in ranks], reverse=True)
        return {"rank": 0, "description": f"High Card", "high_card_values": high_values[:5]}

    @staticmethod
    def _rank_to_value(rank):
        """Convert a card rank to a numeric value."""
        if rank == "A":
            return 14
        elif rank == "K":
            return 13
        elif rank == "Q":
            return 12
        elif rank == "J":
            return 11
        elif rank == "T":
            return 10
        else:
            return int(rank)

    @staticmethod
    def _rank_to_name(value):
        """Convert a numeric value back to a readable card name."""
        if value == 14:
            return "Ace"
        elif value == 13:
            return "King"
        elif value == 12:
            return "Queen"
        elif value == 11:
            return "Jack"
        elif value == 10:
            return "10"
        else:
            return str(value)
