/**
 * Deck class for managing playing cards
 */
class Deck {
    constructor() {
        this.cards = [];
        this.reset();
    }

    /**
     * Reset deck to a new complete set of cards
     */
    reset() {
        this.cards = [];
        const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
        const suits = ['hearts', 'diamonds', 'clubs', 'spades'];

        for (const suit of suits) {
            for (const rank of ranks) {
                this.cards.push(new Card(rank, suit));
            }
        }

        return this;
    }

    /**
     * Shuffle the deck
     * @returns {Deck} - The shuffled deck
     */
    shuffle() {
        for (let i = this.cards.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.cards[i], this.cards[j]] = [this.cards[j], this.cards[i]];
        }
        return this;
    }

    /**
     * Deal a single card from the deck
     * @param {boolean} faceUp - Whether the card should be face up
     * @returns {Card} - The dealt card
     */
    dealCard(faceUp = true) {
        if (this.cards.length === 0) {
            throw new Error("The deck is empty!");
        }

        const card = this.cards.pop();
        card.faceUp = faceUp;
        return card;
    }

    /**
     * Deal a specific number of cards
     * @param {number} numCards - Number of cards to deal
     * @param {boolean} faceUp - Whether the cards should be face up
     * @returns {Card[]} - Array of dealt cards
     */
    dealCards(numCards, faceUp = true) {
        const cards = [];
        for (let i = 0; i < numCards; i++) {
            if (this.cards.length === 0) break;
            cards.push(this.dealCard(faceUp));
        }
        return cards;
    }

    /**
     * Get the number of cards left in the deck
     * @returns {number} - Number of cards
     */
    get remainingCards() {
        return this.cards.length;
    }
}