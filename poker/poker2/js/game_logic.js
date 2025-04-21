/**
 * Game state constants
 */
const GameState = {
    WAITING: 'waiting',
    PREFLOP: 'preflop',
    FLOP: 'flop',
    TURN: 'turn',
    RIVER: 'river',
    SHOWDOWN: 'showdown'
};

/**
 * Player actions
 */
const PlayerAction = {
    FOLD: 'fold',
    CHECK: 'check',
    CALL: 'call',
    BET: 'bet',
    RAISE: 'raise'
};

/**
 * Hand rankings
 */
const HandRank = {
    HIGH_CARD: 0,
    PAIR: 1,
    TWO_PAIR: 2,
    THREE_OF_A_KIND: 3,
    STRAIGHT: 4,
    FLUSH: 5,
    FULL_HOUSE: 6,
    FOUR_OF_A_KIND: 7,
    STRAIGHT_FLUSH: 8,
    ROYAL_FLUSH: 9
};

/**
 * Main game logic class
 */
class PokerGame {
    constructor(playerCount = 4, startingChips = 1000, smallBlind = 5) {
        this.players = [];
        this.deck = new Deck();
        this.communityCards = [];
        this.pot = 0;
        this.currentBet = 0;
        this.smallBlind = smallBlind;
        this.bigBlind = smallBlind * 2;
        this.currentState = GameState.WAITING;
        this.currentPlayerIndex = 0;
        this.dealer = 0;
        this.startingChips = startingChips;

        // Initialize human player
        this.addPlayer('You', true);

        // Initialize AI players
        for (let i = 1; i < playerCount; i++) {
            this.addPlayer(`Player ${i}`, false);
        }
    }

    /**
     * Add a player to the game
     * @param {string} name - Player name
     * @param {boolean} isHuman - Whether this is a human player
     */
    addPlayer(name, isHuman = false) {
        this.players.push({
            name,
            isHuman,
            chips: this.startingChips,
            cards: [],
            bet: 0,
            folded: false,
            handRank: null,
            handDescription: '',
            isAllIn: false
        });
    }

    /**
     * Start a new round of poker
     */
    startNewRound() {
        // Reset game state
        this.deck.reset().shuffle();
        this.communityCards = [];
        this.pot = 0;
        this.currentBet = 0;

        // Reset player state
        this.players.forEach(player => {
            player.cards = [];
            player.bet = 0;
            player.folded = false;
            player.handRank = null;
            player.handDescription = '';
            player.isAllIn = false;
        });

        // Move dealer button
        this.moveDealer();

        // Post blinds
        this.postBlinds();

        // Deal cards
        this.dealHoleCards();

        // Set game state to preflop
        this.currentState = GameState.PREFLOP;

        // Set current player (after big blind)
        this.currentPlayerIndex = (this.dealer + 3) % this.players.length;
        this.adjustCurrentPlayerIfFolded();

        return this.getGameState();
    }

    /**
     * Move dealer position for next round
     */
    moveDealer() {
        this.dealer = (this.dealer + 1) % this.players.length;
    }

    /**
     * Post small and big blinds
     */
    postBlinds() {
        // Small blind (player after dealer)
        const sbIndex = (this.dealer + 1) % this.players.length;
        this.placeBet(sbIndex, this.smallBlind);

        // Big blind (player after small blind)
        const bbIndex = (this.dealer + 2) % this.players.length;
        this.placeBet(bbIndex, this.bigBlind);

        // Set current bet to big blind
        this.currentBet = this.bigBlind;
    }

    /**
     * Deal two cards to each player
     */
    dealHoleCards() {
        for (let i = 0; i < 2; i++) {
            for (let j = 0; j < this.players.length; j++) {
                const playerIndex = (this.dealer + j + 1) % this.players.length;
                const faceUp = this.players[playerIndex].isHuman;
                this.players[playerIndex].cards.push(this.deck.dealCard(faceUp));
            }
        }
    }

    /**
     * Deal the flop (first three community cards)
     */
    dealFlop() {
        // Burn a card
        this.deck.dealCard(false);

        // Deal 3 community cards
        for (let i = 0; i < 3; i++) {
            this.communityCards.push(this.deck.dealCard());
        }

        this.currentState = GameState.FLOP;
        this.resetBettingRound();
    }

    /**
     * Deal the turn (fourth community card)
     */
    dealTurn() {
        // Burn a card
        this.deck.dealCard(false);

        // Deal 1 community card
        this.communityCards.push(this.deck.dealCard());

        this.currentState = GameState.TURN;
        this.resetBettingRound();
    }

    /**
     * Deal the river (fifth community card)
     */
    dealRiver() {
        // Burn a card
        this.deck.dealCard(false);

        // Deal 1 community card
        this.communityCards.push(this.deck.dealCard());

        this.currentState = GameState.RIVER;
        this.resetBettingRound();
    }

    /**
     * Reset betting for a new round (flop, turn, river)
     */
    resetBettingRound() {
        this.currentBet = 0;
        this.players.forEach(player => {
            player.bet = 0;
        });

        // Start with player after dealer
        this.currentPlayerIndex = (this.dealer + 1) % this.players.length;
        this.adjustCurrentPlayerIfFolded();
    }

    /**
     * Skip folded or all-in players
     */
    adjustCurrentPlayerIfFolded() {
        let checkedAll = false;
        let startIndex = this.currentPlayerIndex;

        while (
            (this.players[this.currentPlayerIndex].folded ||
                this.players[this.currentPlayerIndex].isAllIn ||
                this.players[this.currentPlayerIndex].chips === 0) &&
            !checkedAll
        ) {
            this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;

            // If we've gone full circle, all players are folded or all-in
            if (this.currentPlayerIndex === startIndex) {
                checkedAll = true;
                // Move to next stage since no one can act
                if (this.getRemainingPlayers().length <= 1) {
                    this.finishRound();
                } else {
                    this.progressToNextStage();
                }
                break;
            }
        }
    }

    /**
     * Progress to the next stage (preflop -> flop -> turn -> river -> showdown)
     */
    progressToNextStage() {
        // Move all bets to the pot
        this.collectBets();

        switch (this.currentState) {
            case GameState.PREFLOP:
                this.dealFlop();
                break;
            case GameState.FLOP:
                this.dealTurn();
                break;
            case GameState.TURN:
                this.dealRiver();
                break;
            case GameState.RIVER:
                this.showdown();
                break;
        }
    }

    /**
     * Collect all bets into the pot
     */
    collectBets() {
        this.players.forEach(player => {
            this.pot += player.bet;
            player.bet = 0;
        });
        this.currentBet = 0;
    }

    /**
     * Place a bet for a player
     * @param {number} playerIndex - Player index
     * @param {number} amount - Bet amount
     * @returns {number} - Actual bet amount
     */
    placeBet(playerIndex, amount) {
        try {
            const player = this.players[playerIndex];

            // Cap the bet at the player's available chips
            const actualBet = Math.min(amount, player.chips);

            // Safety check
            if (actualBet <= 0) {
                return 0;
            }

            player.chips -= actualBet;
            player.bet += actualBet;

            // Check if player is all in
            if (player.chips === 0) {
                player.isAllIn = true;
            }

            // Update current bet if this is higher
            if (player.bet > this.currentBet) {
                this.currentBet = player.bet;
            }

            return actualBet;
        } catch (error) {
            console.error('Error placing bet:', error);
            return 0;
        }
    }

    /**
     * Process a player action
     * @param {number} action - The PlayerAction to perform
     * @param {number} betAmount - Amount to bet (if applicable)
     * @returns {Object} - Updated game state
     */
    playerAction(action, betAmount = 0) {
        const player = this.players[this.currentPlayerIndex];

        // Safety check - prevent actions with invalid values
        if (!action || typeof action !== 'string') {
            console.error('Invalid action provided:', action);
            return this.getGameState();
        }

        try {
            switch (action) {
                case PlayerAction.FOLD:
                    player.folded = true;
                    break;

                case PlayerAction.CHECK:
                    // Check is only valid if there's no current bet to call
                    if (this.currentBet > player.bet) {
                        console.error('Invalid check - there is a bet to call');
                        return this.getGameState();
                    }
                    break;

                case PlayerAction.CALL:
                    // Call the current bet
                    const callAmount = this.currentBet - player.bet;

                    // Safety check - prevent negative or zero calls
                    if (callAmount <= 0) {
                        console.error('Invalid call amount:', callAmount);
                        return this.getGameState();
                    }

                    this.placeBet(this.currentPlayerIndex, callAmount);
                    break;

                case PlayerAction.BET:
                case PlayerAction.RAISE:
                    // Validate bet amount
                    if (!betAmount || betAmount <= 0) {
                        console.error('Invalid bet amount:', betAmount);
                        return this.getGameState();
                    }

                    // Minimum bet is current bet plus big blind OR double current bet if already a bet
                    let minBet = this.currentBet === 0 ? this.bigBlind : this.currentBet * 2 - player.bet;
                    minBet = Math.min(minBet, player.chips); // Cap at player's chips

                    if (betAmount < minBet) {
                        betAmount = minBet;
                    }

                    this.placeBet(this.currentPlayerIndex, betAmount);
                    break;

                default:
                    console.error('Unknown action:', action);
                    return this.getGameState();
            }

            // Move to next player
            this.nextPlayer();

            // Check if round is complete
            if (this.isBettingRoundComplete()) {
                this.progressToNextStage();
            }

            return this.getGameState();
        } catch (error) {
            console.error('Error processing player action:', error);
            // Return current game state if there was an error
            return this.getGameState();
        }
    }

    /**
     * Move to the next player
     */
    nextPlayer() {
        this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
        this.adjustCurrentPlayerIfFolded();
    }

    /**
     * Check if betting round is complete
     */
    isBettingRoundComplete() {
        const activePlayers = this.players.filter(p => !p.folded && !p.isAllIn);

        // If only 0 or 1 players are active, round is complete
        if (activePlayers.length <= 1) {
            return true;
        }

        // Check if all active players have bet the same amount
        const targetBet = this.currentBet;
        const allBetsEqual = activePlayers.every(p => p.bet === targetBet);

        // Complete if all active players have acted and all bets are equal
        return allBetsEqual && this.allPlayersHaveActed();
    }

    /**
     * Check if all players have had a chance to act in this betting round
     */
    allPlayersHaveActed() {
        // This is simplified logic - would need to track who has acted in a real implementation
        return true;
    }

    /**
     * Get the number of players still in the hand
     * @returns {number} - Count of non-folded players
     */
    getRemainingPlayers() {
        return this.players.filter(player => !player.folded);
    }

    /**
     * End the round with a showdown
     */
    showdown() {
        this.currentState = GameState.SHOWDOWN;

        // Reveal all cards
        this.players.forEach(player => {
            player.cards.forEach(card => {
                card.faceUp = true;
            });
        });

        // Evaluate hands
        this.evaluateHands();

        // Determine winner
        const winners = this.determineWinners();

        // Distribute pot
        this.distributePot(winners);

        return winners;
    }

    /**
     * Finish the round early (e.g., when all but one player has folded)
     */
    finishRound() {
        const remainingPlayers = this.getRemainingPlayers();

        if (remainingPlayers.length === 1) {
            // Last player standing wins
            const winner = remainingPlayers[0];
            winner.chips += this.pot;
            this.pot = 0;
            this.currentState = GameState.WAITING;
            return [winner];
        } else if (remainingPlayers.length > 1) {
            // We need a showdown between remaining players
            return this.showdown();
        }

        // Shouldn't get here
        return [];
    }

    /**
     * Evaluate all players' hands
     */
    evaluateHands() {
        this.getRemainingPlayers().forEach(player => {
            const hand = this.evaluateHand([...player.cards, ...this.communityCards]);
            player.handRank = hand.rank;
            player.handDescription = hand.description;
        });
    }

    /**
     * Evaluate a 7-card hand to find the best 5-card poker hand
     * @param {Card[]} cards - Array of 7 cards
     * @returns {Object} - Hand rank and description
     */
    evaluateHand(cards) {
        // Sort cards by value (descending)
        const sortedCards = [...cards].sort((a, b) => b.value - a.value);

        // Check for each hand rank from highest to lowest
        if (this.hasRoyalFlush(sortedCards)) {
            return { rank: HandRank.ROYAL_FLUSH, description: 'Royal Flush' };
        }

        const straightFlush = this.hasStraightFlush(sortedCards);
        if (straightFlush.has) {
            return { rank: HandRank.STRAIGHT_FLUSH, description: `Straight Flush, ${straightFlush.high} high` };
        }

        const fourOfAKind = this.hasFourOfAKind(sortedCards);
        if (fourOfAKind.has) {
            return { rank: HandRank.FOUR_OF_A_KIND, description: `Four of a Kind, ${fourOfAKind.value}s` };
        }

        const fullHouse = this.hasFullHouse(sortedCards);
        if (fullHouse.has) {
            return { rank: HandRank.FULL_HOUSE, description: `Full House, ${fullHouse.three}s over ${fullHouse.two}s` };
        }

        const flush = this.hasFlush(sortedCards);
        if (flush.has) {
            return { rank: HandRank.FLUSH, description: `Flush, ${this.cardValueToString(flush.high)} high` };
        }

        const straight = this.hasStraight(sortedCards);
        if (straight.has) {
            return { rank: HandRank.STRAIGHT, description: `Straight, ${this.cardValueToString(straight.high)} high` };
        }

        const threeOfAKind = this.hasThreeOfAKind(sortedCards);
        if (threeOfAKind.has) {
            return { rank: HandRank.THREE_OF_A_KIND, description: `Three of a Kind, ${this.cardValueToString(threeOfAKind.value)}s` };
        }

        const twoPair = this.hasTwoPair(sortedCards);
        if (twoPair.has) {
            return { rank: HandRank.TWO_PAIR, description: `Two Pair, ${this.cardValueToString(twoPair.high)}s and ${this.cardValueToString(twoPair.low)}s` };
        }

        const pair = this.hasPair(sortedCards);
        if (pair.has) {
            return { rank: HandRank.PAIR, description: `Pair of ${this.cardValueToString(pair.value)}s` };
        }

        return { rank: HandRank.HIGH_CARD, description: `High Card ${this.cardValueToString(sortedCards[0].value)}` };
    }

    /**
     * Convert card numeric value to string representation
     * @param {number} value - Card value
     * @returns {string} - String representation
     */
    cardValueToString(value) {
        switch (value) {
            case 14: return 'A';
            case 13: return 'K';
            case 12: return 'Q';
            case 11: return 'J';
            default: return value.toString();
        }
    }

    /**
     * Check for royal flush
     * @param {Card[]} cards - Sorted cards
     * @returns {boolean} - True if hand contains a royal flush
     */
    hasRoyalFlush(cards) {
        // Need A, K, Q, J, 10 of same suit
        const bySuit = this.groupBySuit(cards);

        for (const suit in bySuit) {
            if (bySuit[suit].length >= 5) {
                const values = bySuit[suit].map(c => c.value);
                if (
                    values.includes(14) && // A
                    values.includes(13) && // K
                    values.includes(12) && // Q
                    values.includes(11) && // J
                    values.includes(10)    // 10
                ) {
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Check for straight flush
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has straight flush and high card
     */
    hasStraightFlush(cards) {
        const bySuit = this.groupBySuit(cards);

        for (const suit in bySuit) {
            if (bySuit[suit].length >= 5) {
                const suitCards = bySuit[suit].sort((a, b) => b.value - a.value);
                const straight = this.hasStraight(suitCards);
                if (straight.has) {
                    return { has: true, high: straight.high };
                }
            }
        }

        return { has: false };
    }

    /**
     * Check for four of a kind
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has four of a kind and value
     */
    hasFourOfAKind(cards) {
        const groups = this.groupByValue(cards);

        for (const value in groups) {
            if (groups[value].length === 4) {
                return { has: true, value: parseInt(value) };
            }
        }

        return { has: false };
    }

    /**
     * Check for full house
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has full house, three of kind value, pair value
     */
    hasFullHouse(cards) {
        const groups = this.groupByValue(cards);
        let three = null;
        let two = null;

        // Find highest three of a kind
        for (const value in groups) {
            if (groups[value].length >= 3) {
                three = Math.max(three || 0, parseInt(value));
            }
        }

        // Find highest pair (different from three of a kind)
        for (const value in groups) {
            if (groups[value].length >= 2 && parseInt(value) !== three) {
                two = Math.max(two || 0, parseInt(value));
            }
        }

        if (three !== null && two !== null) {
            return { has: true, three, two };
        }

        return { has: false };
    }

    /**
     * Check for flush
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has flush and high card
     */
    hasFlush(cards) {
        const bySuit = this.groupBySuit(cards);

        for (const suit in bySuit) {
            if (bySuit[suit].length >= 5) {
                // Get highest 5 cards of the flush
                const flushCards = bySuit[suit].sort((a, b) => b.value - a.value).slice(0, 5);
                return { has: true, high: flushCards[0].value };
            }
        }

        return { has: false };
    }

    /**
     * Check for straight
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has straight and high card
     */
    hasStraight(cards) {
        // Get unique values and sort descending
        const uniqueValues = [...new Set(cards.map(c => c.value))].sort((a, b) => b - a);

        // Special case for A-5 straight (where A is treated as 1)
        if (
            uniqueValues.includes(14) && // A
            uniqueValues.includes(5) &&
            uniqueValues.includes(4) &&
            uniqueValues.includes(3) &&
            uniqueValues.includes(2)
        ) {
            return { has: true, high: 5 };
        }

        // Check for normal straights
        for (let i = 0; i <= uniqueValues.length - 5; i++) {
            if (uniqueValues[i] === uniqueValues[i + 4] + 4) {
                return { has: true, high: uniqueValues[i] };
            }
        }

        return { has: false };
    }

    /**
     * Check for three of a kind
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has three of a kind and value
     */
    hasThreeOfAKind(cards) {
        const groups = this.groupByValue(cards);

        for (const value in groups) {
            if (groups[value].length === 3) {
                return { has: true, value: parseInt(value) };
            }
        }

        return { has: false };
    }

    /**
     * Check for two pair
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has two pair, high pair value, low pair value
     */
    hasTwoPair(cards) {
        const groups = this.groupByValue(cards);
        const pairs = [];

        for (const value in groups) {
            if (groups[value].length === 2) {
                pairs.push(parseInt(value));
            }
        }

        if (pairs.length >= 2) {
            pairs.sort((a, b) => b - a);
            return { has: true, high: pairs[0], low: pairs[1] };
        }

        return { has: false };
    }

    /**
     * Check for pair
     * @param {Card[]} cards - Sorted cards
     * @returns {Object} - Has pair and value
     */
    hasPair(cards) {
        const groups = this.groupByValue(cards);

        for (const value in groups) {
            if (groups[value].length === 2) {
                return { has: true, value: parseInt(value) };
            }
        }

        return { has: false };
    }

    /**
     * Group cards by suit
     * @param {Card[]} cards - Cards to group
     * @returns {Object} - Cards grouped by suit
     */
    groupBySuit(cards) {
        const result = {};

        cards.forEach(card => {
            if (!result[card.suit]) {
                result[card.suit] = [];
            }

            result[card.suit].push(card);
        });

        return result;
    }

    /**
     * Group cards by value
     * @param {Card[]} cards - Cards to group
     * @returns {Object} - Cards grouped by value
     */
    groupByValue(cards) {
        const result = {};

        cards.forEach(card => {
            const value = card.value.toString();

            if (!result[value]) {
                result[value] = [];
            }

            result[value].push(card);
        });

        return result;
    }

    /**
     * Determine winners of the hand
     * @returns {Array} - Array of winning players
     */
    determineWinners() {
        const activePlayers = this.getRemainingPlayers();

        if (activePlayers.length === 0) {
            return [];
        }

        if (activePlayers.length === 1) {
            return [activePlayers[0]];
        }

        let highestRank = -1;
        let winners = [];

        // Find highest hand rank
        activePlayers.forEach(player => {
            if (player.handRank > highestRank) {
                highestRank = player.handRank;
                winners = [player];
            } else if (player.handRank === highestRank) {
                winners.push(player);
            }
        });

        // TODO: Handle ties with kickers

        return winners;
    }

    /**
     * Distribute pot to winner(s)
     * @param {Array} winners - Array of winning players
     */
    distributePot(winners) {
        if (winners.length === 0) {
            return;
        }

        const winAmount = Math.floor(this.pot / winners.length);

        winners.forEach(winner => {
            winner.chips += winAmount;
        });

        // Any remaining chips go to the first winner (due to rounding)
        const remainder = this.pot - (winAmount * winners.length);
        if (remainder > 0 && winners.length > 0) {
            winners[0].chips += remainder;
        }

        this.pot = 0;
    }

    /**
     * Get current game state for UI
     */
    getGameState() {
        return {
            players: this.players,
            communityCards: this.communityCards,
            pot: this.pot,
            currentBet: this.currentBet,
            currentState: this.currentState,
            currentPlayer: this.players[this.currentPlayerIndex],
            dealer: this.dealer,
            smallBlind: this.smallBlind,
            bigBlind: this.bigBlind
        };
    }
}