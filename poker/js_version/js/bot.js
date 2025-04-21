/**
 * Poker bot class for AI opponents
 */
class PokerBot {
    /**
     * Create a new poker bot
     * @param {string} difficultyLevel - Bot difficulty: 'easy', 'medium', or 'hard'
     */
    constructor(difficultyLevel = 'medium') {
        this.difficultyLevel = difficultyLevel;
        // Store hand strength thresholds based on difficulty
        this.thresholds = this.getThresholds(difficultyLevel);
    }

    /**
     * Set thresholds based on difficulty level
     * @param {string} difficultyLevel - Bot difficulty level
     * @returns {Object} - Thresholds for different actions
     */
    getThresholds(difficultyLevel) {
        switch (difficultyLevel) {
            case 'easy':
                return {
                    fold: 0.2,   // Fold with hands below this strength
                    call: 0.4,   // Call with hands between fold and call
                    raise: 0.7,  // Raise with hands between call and raise, all-in above raise
                    bluffFrequency: 0.1  // How often the bot bluffs
                };
            case 'hard':
                return {
                    fold: 0.15,
                    call: 0.5,
                    raise: 0.75,
                    bluffFrequency: 0.3
                };
            case 'medium':
            default:
                return {
                    fold: 0.18,
                    call: 0.45,
                    raise: 0.72,
                    bluffFrequency: 0.2
                };
        }
    }

    /**
     * Decide on an action based on game state
     * @param {Object} gameState - Current game state
     * @param {number} botIndex - Index of the bot in the player array
     * @returns {Object} - Action and bet amount
     */
    decideAction(gameState, botIndex) {
        const player = gameState.players[botIndex];
        const handStrength = this.evaluateHandStrength(player.cards, gameState.communityCards, gameState.currentState);

        // Add a random element for unpredictability
        const isBluffing = Math.random() < this.thresholds.bluffFrequency;

        // Adjust hand strength based on bluffing
        const effectiveStrength = isBluffing
            ? (1 - handStrength) // When bluffing, act opposite to hand strength
            : handStrength;

        // Check if player can check (no current bet)
        const canCheck = player.bet === gameState.currentBet;

        // Calculate pot odds if there's a bet to call
        const betToCall = gameState.currentBet - player.bet;
        const potOdds = betToCall > 0 ? betToCall / (gameState.pot + betToCall) : 0;

        // Calculate position advantage (higher is better)
        const playersRemaining = this.countPlayersAfter(gameState, botIndex);
        const positionAdvantage = 1 - (playersRemaining / (gameState.players.length - 1));

        // Adjust thresholds based on position and pot odds
        const adjustedThresholds = this.adjustThresholds(this.thresholds, positionAdvantage, potOdds);

        // Decide on action based on hand strength and adjusted thresholds
        let action, betAmount = 0;

        if (effectiveStrength < adjustedThresholds.fold) {
            // Weak hand, fold if there's a bet or check if possible
            action = canCheck ? PlayerAction.CHECK : PlayerAction.FOLD;
        }
        else if (effectiveStrength < adjustedThresholds.call) {
            // Medium hand, call/check
            action = canCheck ? PlayerAction.CHECK : PlayerAction.CALL;
        }
        else if (effectiveStrength < adjustedThresholds.raise) {
            // Strong hand, bet/raise
            action = canCheck ? PlayerAction.BET : PlayerAction.RAISE;
            betAmount = this.calculateBetSize(gameState, player, effectiveStrength, 'normal');
        }
        else {
            // Very strong hand, bet/raise big
            action = canCheck ? PlayerAction.BET : PlayerAction.RAISE;
            betAmount = this.calculateBetSize(gameState, player, effectiveStrength, 'large');
        }

        // Add some randomness to the final decision
        if (Math.random() < 0.1) {
            action = this.getRandomAction(canCheck);
            if (action === PlayerAction.BET || action === PlayerAction.RAISE) {
                betAmount = this.calculateBetSize(gameState, player, Math.random(), 'random');
            }
        }

        return { action, betAmount };
    }

    /**
     * Count how many players will act after this bot
     * @param {Object} gameState - Current game state
     * @param {number} botIndex - Index of the bot
     * @returns {number} - Number of players yet to act
     */
    countPlayersAfter(gameState, botIndex) {
        let count = 0;
        let currentIndex = (botIndex + 1) % gameState.players.length;

        while (currentIndex !== gameState.currentPlayerIndex) {
            if (!gameState.players[currentIndex].folded && !gameState.players[currentIndex].isAllIn) {
                count++;
            }
            currentIndex = (currentIndex + 1) % gameState.players.length;
        }

        return count;
    }

    /**
     * Adjust thresholds based on position and pot odds
     * @param {Object} baseThresholds - Base thresholds
     * @param {number} positionAdvantage - Position advantage factor
     * @param {number} potOdds - Pot odds
     * @returns {Object} - Adjusted thresholds
     */
    adjustThresholds(baseThresholds, positionAdvantage, potOdds) {
        // In late position (high advantage), we can play more hands
        // With good pot odds, we can call with weaker hands
        return {
            fold: Math.max(0.1, baseThresholds.fold - (positionAdvantage * 0.1) - (potOdds * 0.2)),
            call: Math.max(0.2, baseThresholds.call - (positionAdvantage * 0.1) - (potOdds * 0.3)),
            raise: Math.max(0.4, baseThresholds.raise - (positionAdvantage * 0.05)),
            bluffFrequency: baseThresholds.bluffFrequency + (positionAdvantage * 0.1)
        };
    }

    /**
     * Calculate a bet size based on hand strength and strategy
     * @param {Object} gameState - Current game state
     * @param {Object} player - Player making the bet
     * @param {number} handStrength - Strength of the hand
     * @param {string} betSizing - Sizing strategy ('small', 'normal', 'large', 'random')
     * @returns {number} - Bet amount
     */
    calculateBetSize(gameState, player, handStrength, betSizing) {
        const pot = gameState.pot;
        const minBet = gameState.currentBet > 0 ? gameState.currentBet * 2 : gameState.bigBlind;
        const maxBet = player.chips;

        let betSize;

        switch (betSizing) {
            case 'small':
                betSize = Math.max(minBet, pot * 0.5);
                break;
            case 'normal':
                betSize = Math.max(minBet, pot * 0.75);
                break;
            case 'large':
                betSize = Math.max(minBet, pot * (1 + handStrength));
                break;
            case 'random':
                const randomFactor = 0.5 + Math.random();
                betSize = Math.max(minBet, pot * randomFactor);
                break;
            default:
                betSize = minBet;
        }

        // Round to nearest big blind for more realistic betting
        const bigBlind = gameState.bigBlind;
        betSize = Math.round(betSize / bigBlind) * bigBlind;

        // Cap at player's remaining chips
        return Math.min(betSize, maxBet);
    }

    /**
     * Get a random action for unpredictable play
     * @param {boolean} canCheck - Whether check is available
     * @returns {string} - Random action
     */
    getRandomAction(canCheck) {
        const actions = [PlayerAction.FOLD];

        if (canCheck) {
            actions.push(PlayerAction.CHECK);
            actions.push(PlayerAction.BET);
        } else {
            actions.push(PlayerAction.CALL);
            actions.push(PlayerAction.RAISE);
        }

        const randomIndex = Math.floor(Math.random() * actions.length);
        return actions[randomIndex];
    }

    /**
     * Evaluate the strength of a hand
     * @param {Array} holeCards - Player's hole cards
     * @param {Array} communityCards - Community cards
     * @param {string} gameStage - Current game stage
     * @returns {number} - Hand strength between 0 and 1
     */
    evaluateHandStrength(holeCards, communityCards, gameStage) {
        // Pre-flop strength is based on hole cards only
        if (gameStage === GameState.PREFLOP) {
            return this.evaluatePreFlopStrength(holeCards);
        }

        // Simplified implementation for post-flop hand strength
        // Real implementation would simulate possible hands or use a lookup table

        // Make 7 card hand if possible (for turn and river)
        const allCards = [...holeCards, ...communityCards];

        // Count paired cards, flush draws, straight draws
        const valuesCount = this.countCardValues(allCards);
        const suitsCount = this.countCardSuits(allCards);

        // Check for made hands
        if (this.hasStraightFlushDraw(allCards)) return 0.95;
        if (this.hasFourOfAKind(valuesCount)) return 0.9;
        if (this.hasFullHouse(valuesCount)) return 0.85;
        if (this.hasFlush(suitsCount)) return 0.8;
        if (this.hasStraight(allCards)) return 0.75;
        if (this.hasThreeOfAKind(valuesCount)) return 0.7;
        if (this.hasTwoPair(valuesCount)) return 0.6;
        if (this.hasPair(valuesCount)) return 0.5;

        // Check for strong draws
        if (this.hasFlushDraw(suitsCount)) return 0.4;
        if (this.hasStraightDraw(allCards)) return 0.35;
        if (this.hasOvercards(holeCards, communityCards)) return 0.3;

        // Weak hand
        return 0.2;
    }

    /**
     * Evaluate pre-flop hand strength
     * @param {Array} holeCards - Player's hole cards
     * @returns {number} - Hand strength between 0 and 1
     */
    evaluatePreFlopStrength(holeCards) {
        if (!holeCards || holeCards.length !== 2) return 0;

        const card1 = holeCards[0];
        const card2 = holeCards[1];

        const isPair = card1.value === card2.value;
        const isSuited = card1.suit === card2.suit;
        const highCard = Math.max(card1.value, card2.value);
        const lowCard = Math.min(card1.value, card2.value);
        const gapSize = highCard - lowCard - 1;

        // High pairs are very strong
        if (isPair) {
            if (highCard >= 10) return 0.9;  // AA, KK, QQ, JJ, 10-10
            if (highCard >= 7) return 0.7;   // 99, 88, 77
            return 0.5 + (highCard / 20);    // Scale smaller pairs
        }

        // High cards
        if (highCard >= 13) {  // Ace high
            if (lowCard >= 12) return 0.8;   // AK
            if (lowCard >= 10) return isSuited ? 0.7 : 0.6;  // AQ, AJ, AT
            if (isSuited) return 0.5;        // Ax suited
            return 0.3;                      // Ax offsuit
        }

        if (highCard === 12) {  // King high
            if (lowCard >= 10) return isSuited ? 0.65 : 0.55;  // KQ, KJ, KT
            if (isSuited) return 0.4;        // Kx suited
            return 0.25;                     // Kx offsuit
        }

        // Connected cards have more value
        if (gapSize === 0) {
            return isSuited ? 0.5 : 0.35;    // Connected cards
        }

        // One gap connectors
        if (gapSize === 1) {
            return isSuited ? 0.4 : 0.25;    // One-gap connectors
        }

        // Suited cards have some value
        if (isSuited) {
            return 0.3;
        }

        // Everything else is weak
        return 0.15;
    }

    /**
     * Count occurrences of each card value
     * @param {Array} cards - Array of cards
     * @returns {Object} - Map of value to count
     */
    countCardValues(cards) {
        const valuesCount = {};

        cards.forEach(card => {
            const value = card.value;
            valuesCount[value] = (valuesCount[value] || 0) + 1;
        });

        return valuesCount;
    }

    /**
     * Count occurrences of each suit
     * @param {Array} cards - Array of cards
     * @returns {Object} - Map of suit to count
     */
    countCardSuits(cards) {
        const suitsCount = {};

        cards.forEach(card => {
            const suit = card.suit;
            suitsCount[suit] = (suitsCount[suit] || 0) + 1;
        });

        return suitsCount;
    }

    /* Hand evaluation helper methods */

    hasPair(valuesCount) {
        return Object.values(valuesCount).some(count => count >= 2);
    }

    hasTwoPair(valuesCount) {
        return Object.values(valuesCount).filter(count => count >= 2).length >= 2;
    }

    hasThreeOfAKind(valuesCount) {
        return Object.values(valuesCount).some(count => count >= 3);
    }

    hasFourOfAKind(valuesCount) {
        return Object.values(valuesCount).some(count => count >= 4);
    }

    hasFullHouse(valuesCount) {
        const counts = Object.values(valuesCount);
        return counts.some(count => count >= 3) && counts.filter(count => count >= 2).length >= 2;
    }

    hasFlush(suitsCount) {
        return Object.values(suitsCount).some(count => count >= 5);
    }

    hasFlushDraw(suitsCount) {
        return Object.values(suitsCount).some(count => count === 4);
    }

    hasStraight(cards) {
        const values = [...new Set(cards.map(c => c.value))].sort((a, b) => a - b);

        // Check for A-5 straight
        if (values.includes(14) && values.includes(2) && values.includes(3) &&
            values.includes(4) && values.includes(5)) {
            return true;
        }

        // Check for other straights
        for (let i = 0; i <= values.length - 5; i++) {
            if (values[i + 4] - values[i] === 4) {
                return true;
            }
        }

        return false;
    }

    hasStraightDraw(cards) {
        // Very simplified straight draw check (would be improved in real implementation)
        const uniqueValues = [...new Set(cards.map(c => c.value))].sort((a, b) => a - b);

        // Count consecutive values
        let maxConsecutive = 1;
        let current = 1;

        for (let i = 1; i < uniqueValues.length; i++) {
            if (uniqueValues[i] === uniqueValues[i - 1] + 1) {
                current++;
                maxConsecutive = Math.max(maxConsecutive, current);
            } else if (uniqueValues[i] !== uniqueValues[i - 1]) {
                current = 1;
            }
        }

        return maxConsecutive === 4; // Open-ended or gutshot straight draw
    }

    hasStraightFlushDraw(cards) {
        const bySuit = {};

        // Group cards by suit
        cards.forEach(card => {
            if (!bySuit[card.suit]) {
                bySuit[card.suit] = [];
            }
            bySuit[card.suit].push(card);
        });

        // Check each suit group for a straight
        for (const suit in bySuit) {
            if (bySuit[suit].length >= 5) {
                if (this.hasStraight(bySuit[suit])) {
                    return true;
                }
            }
        }

        return false;
    }

    hasOvercards(holeCards, communityCards) {
        if (!communityCards || communityCards.length === 0) return false;

        // Find highest community card
        const maxCommunityValue = Math.max(...communityCards.map(c => c.value));

        // Check if either hole card is higher than all community cards
        return holeCards.some(card => card.value > maxCommunityValue);
    }
}