/**
 * Card class representing a playing card
 */
class Card {
    constructor(rank, suit) {
        this.rank = rank;
        this.suit = suit;
        this.faceUp = true;
    }

    /**
     * Get the value of the card (used for hand evaluation)
     * @returns {number} - Card value
     */
    get value() {
        switch (this.rank) {
            case 'A': return 14;
            case 'K': return 13;
            case 'Q': return 12;
            case 'J': return 11;
            default: return parseInt(this.rank);
        }
    }

    /**
     * Get card display value
     * @returns {string} - Display value
     */
    get displayRank() {
        return this.rank;
    }

    /**
     * Get the suit symbol
     * @returns {string} - Unicode symbol for the suit
     */
    get suitSymbol() {
        switch (this.suit) {
            case 'hearts': return '♥';
            case 'diamonds': return '♦';
            case 'clubs': return '♣';
            case 'spades': return '♠';
            default: return '';
        }
    }

    /**
     * Get the color of the card
     * @returns {string} - 'red' or 'black'
     */
    get color() {
        return ['hearts', 'diamonds'].includes(this.suit) ? 'red' : 'black';
    }

    /**
     * Flip the card over
     */
    flip() {
        this.faceUp = !this.faceUp;
        return this;
    }

    /**
     * Create HTML element for the card
     * @returns {HTMLElement} - DOM element representing the card
     */
    createCardElement() {
        const cardElement = document.createElement('div');
        cardElement.className = `card ${this.color}`;

        if (!this.faceUp) {
            cardElement.classList.add('face-down');
            return cardElement;
        }

        const topValue = document.createElement('div');
        topValue.className = 'card-value';
        topValue.textContent = this.displayRank;

        const suitElement = document.createElement('div');
        suitElement.className = 'card-suit';
        suitElement.textContent = this.suitSymbol;

        const bottomValue = document.createElement('div');
        bottomValue.className = 'card-back-value';
        bottomValue.textContent = this.displayRank;

        cardElement.appendChild(topValue);
        cardElement.appendChild(suitElement);
        cardElement.appendChild(bottomValue);

        return cardElement;
    }

    /**
     * String representation of the card
     * @returns {string} - String representation
     */
    toString() {
        return `${this.displayRank}${this.suitSymbol}`;
    }
}