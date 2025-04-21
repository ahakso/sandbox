/**
 * UI class to handle the user interface for the poker game
 */
class PokerUI {
    constructor() {
        this.gameState = null;
        this.game = null;
        this.bot = new PokerBot('medium');

        this.communityCardsContainer = document.getElementById('community-cards');
        this.playerCardsContainer = document.getElementById('player-cards');
        this.opponentsContainer = document.getElementById('opponents-container');
        this.potAmount = document.getElementById('pot-amount');
        this.playerChips = document.getElementById('player-chips');
        this.currentPlayerDisplay = document.getElementById('current-player');
        this.gameMessages = document.getElementById('game-messages');
        this.betAmount = document.getElementById('bet-amount');
        this.betSlider = document.getElementById('bet-slider');

        // Action buttons
        this.btnFold = document.getElementById('btn-fold');
        this.btnCheck = document.getElementById('btn-check');
        this.btnCall = document.getElementById('btn-call');
        this.btnBet = document.getElementById('btn-bet');
        this.btnNewGame = document.getElementById('btn-new-game');

        // Add error handling and timeout tracking
        this.isProcessing = false;
        this.timeouts = [];

        this.initEventListeners();
    }

    /**
     * Initialize event listeners for UI elements
     */
    initEventListeners() {
        // Game control
        this.btnNewGame.addEventListener('click', () => this.startNewGame());

        // Player action buttons - add debouncing to prevent multiple rapid clicks
        this.btnFold.addEventListener('click', () => {
            if (!this.isProcessing) this.handlePlayerAction(PlayerAction.FOLD);
        });

        this.btnCheck.addEventListener('click', () => {
            if (!this.isProcessing) this.handlePlayerAction(PlayerAction.CHECK);
        });

        this.btnCall.addEventListener('click', () => {
            if (!this.isProcessing) this.handlePlayerAction(PlayerAction.CALL);
        });

        this.btnBet.addEventListener('click', () => {
            if (!this.isProcessing) {
                const betValue = parseInt(this.betSlider.value);
                this.handlePlayerAction(PlayerAction.BET, betValue);
            }
        });

        // Bet slider
        this.betSlider.addEventListener('input', () => {
            this.betAmount.textContent = `$${this.betSlider.value}`;
        });
    }

    /**
     * Clear all pending timeouts
     */
    clearAllTimeouts() {
        this.timeouts.forEach(timeoutId => clearTimeout(timeoutId));
        this.timeouts = [];
    }

    /**
     * Start a new poker game
     */
    startNewGame() {
        // Clear any pending operations from previous games
        this.clearAllTimeouts();
        this.isProcessing = false;

        // Create a new game with 4 players (1 human + 3 bots)
        this.game = new PokerGame(4, 1000, 5);

        // Start the first round
        this.gameState = this.game.startNewRound();

        // Update the UI
        this.updateUI();

        this.showMessage('New game started! Place your bets.');

        // If the current player is a bot, make its move
        this.processNextAction();
    }

    /**
     * Handle a player action
     * @param {string} action - The action to take (fold, check, call, bet)
     * @param {number} betAmount - Amount to bet (if applicable)
     */
    handlePlayerAction(action, betAmount = 0) {
        if (!this.game || !this.gameState) {
            this.showMessage('Please start a new game first.');
            return;
        }

        // Prevent multiple actions being processed at once
        if (this.isProcessing) {
            return;
        }

        // Flag that we're processing an action
        this.isProcessing = true;

        // Ensure it's the human player's turn
        if (!this.gameState.currentPlayer.isHuman) {
            this.showMessage("It's not your turn!");
            this.isProcessing = false;
            return;
        }

        try {
            // Disable buttons immediately to prevent multiple clicks
            this.disableAllActionButtons();

            // Process the action
            this.gameState = this.game.playerAction(action, betAmount);

            // Update action message
            this.showActionMessage(action, this.gameState.players[0], betAmount);

            // Update the UI
            this.updateUI();

            // Process next actions (bots)
            const timeoutId = setTimeout(() => {
                this.processNextAction();
                this.isProcessing = false;
            }, 500);

            this.timeouts.push(timeoutId);

        } catch (error) {
            console.error("Error processing player action:", error);
            this.showMessage("An error occurred. Please try again.");
            this.isProcessing = false;
            // Re-enable buttons on error
            this.updateActionButtons();
        }
    }

    /**
     * Process next player action (handle bots automatically)
     */
    processNextAction() {
        if (!this.game || !this.gameState) return;

        // If the game is in waiting state (between rounds) or showdown, don't process actions
        if (this.gameState.currentState === GameState.WAITING ||
            this.gameState.currentState === GameState.SHOWDOWN) {
            this.isProcessing = false;
            return;
        }

        // If current player is a bot, make its move
        if (!this.gameState.currentPlayer.isHuman) {
            this.processBotAction();
        } else {
            // If it's the human player's turn, enable the appropriate action buttons
            this.updateActionButtons();
            this.isProcessing = false;
        }
    }

    /**
     * Process bot action automatically
     */
    processBotAction() {
        try {
            const botIndex = this.game.currentPlayerIndex;
            const botDecision = this.bot.decideAction(this.gameState, botIndex);

            // Show bot "thinking"
            this.showMessage(`${this.gameState.currentPlayer.name} is thinking...`);

            // Delay the bot action for more natural gameplay
            const timeoutId = setTimeout(() => {
                try {
                    // Execute bot action
                    this.gameState = this.game.playerAction(botDecision.action, botDecision.betAmount);

                    // Show action message
                    this.showActionMessage(botDecision.action, this.gameState.players[botIndex], botDecision.betAmount);

                    // Update UI
                    this.updateUI();

                    // Process next action
                    const nextTimeoutId = setTimeout(() => {
                        this.processNextAction();
                    }, 500);

                    this.timeouts.push(nextTimeoutId);

                } catch (error) {
                    console.error("Error processing bot action:", error);
                    this.showMessage("An error occurred with bot actions. Starting a new round.");
                    this.isProcessing = false;
                }
            }, 800); // Reduced from 1000ms to 800ms for better pace

            this.timeouts.push(timeoutId);

        } catch (error) {
            console.error("Error in bot decision making:", error);
            this.showMessage("An error occurred with bot decisions. Please try again.");
            this.isProcessing = false;
        }
    }

    /**
     * Display a message about the action taken
     * @param {string} action - The action taken
     * @param {Object} player - The player who took the action
     * @param {number} amount - Bet amount (if applicable)
     */
    showActionMessage(action, player, amount = 0) {
        let message = `${player.name} `;

        switch (action) {
            case PlayerAction.FOLD:
                message += 'folds.';
                break;
            case PlayerAction.CHECK:
                message += 'checks.';
                break;
            case PlayerAction.CALL:
                message += `calls $${this.gameState.currentBet}.`;
                break;
            case PlayerAction.BET:
            case PlayerAction.RAISE:
                message += `${action === PlayerAction.BET ? 'bets' : 'raises'} $${amount}.`;
                break;
        }

        this.showMessage(message);
    }

    /**
     * Update the entire UI based on the current game state
     */
    updateUI() {
        if (!this.gameState) return;

        try {
            // Update pot
            this.potAmount.textContent = this.gameState.pot;

            // Update player chips
            const humanPlayer = this.gameState.players.find(p => p.isHuman);
            if (humanPlayer) {
                this.playerChips.textContent = humanPlayer.chips;
            }

            // Update current player display
            if (this.gameState.currentPlayer) {
                this.currentPlayerDisplay.textContent = this.gameState.currentPlayer.name;
            }

            // Update community cards
            this.updateCommunityCards();

            // Update player cards
            this.updatePlayerCards();

            // Update opponent cards and info
            this.updateOpponents();

            // Update bet slider max value
            if (humanPlayer) {
                this.betSlider.max = humanPlayer.chips;
                this.betSlider.value = Math.min(
                    Math.max(this.gameState.currentBet * 2, this.gameState.bigBlind),
                    humanPlayer.chips
                );
                this.betAmount.textContent = `$${this.betSlider.value}`;
            }

            // Update action buttons based on valid actions
            this.updateActionButtons();

            // Check if the round is over
            if (this.gameState.currentState === GameState.SHOWDOWN) {
                this.handleShowdown();
            }

        } catch (error) {
            console.error("Error updating UI:", error);
            // Don't show an error message here to avoid spamming
        }
    }

    /**
     * Update the community cards display
     */
    updateCommunityCards() {
        // Clear existing cards
        this.communityCardsContainer.innerHTML = '';

        // Add community cards
        this.gameState.communityCards.forEach(card => {
            const cardElement = card.createCardElement();
            cardElement.classList.add('card-dealt');
            this.communityCardsContainer.appendChild(cardElement);
        });

        // Add placeholders for unrevealed cards
        const remainingCards = 5 - this.gameState.communityCards.length;
        for (let i = 0; i < remainingCards; i++) {
            const placeholder = document.createElement('div');
            placeholder.className = 'card placeholder';
            this.communityCardsContainer.appendChild(placeholder);
        }
    }

    /**
     * Update the player's cards display
     */
    updatePlayerCards() {
        // Clear existing cards
        this.playerCardsContainer.innerHTML = '';

        // Find the human player
        const humanPlayer = this.gameState.players.find(p => p.isHuman);

        // Add player cards
        humanPlayer.cards.forEach(card => {
            const cardElement = card.createCardElement();
            cardElement.classList.add('card-dealt');
            this.playerCardsContainer.appendChild(cardElement);
        });
    }

    /**
     * Update the opponents' display
     */
    updateOpponents() {
        // Clear existing opponents
        this.opponentsContainer.innerHTML = '';

        // Add bot players
        this.gameState.players.forEach((player, index) => {
            if (!player.isHuman) {
                const opponentElement = document.createElement('div');
                opponentElement.className = 'player';

                if (index === this.game.currentPlayerIndex) {
                    opponentElement.classList.add('active-player');
                }

                if (player.folded) {
                    opponentElement.classList.add('folded');
                }

                // Add player info
                const nameElement = document.createElement('div');
                nameElement.className = 'player-name';
                nameElement.textContent = player.name;

                const chipsElement = document.createElement('div');
                chipsElement.className = 'player-chips';
                chipsElement.textContent = `$${player.chips}`;

                const betElement = document.createElement('div');
                betElement.className = 'player-bet';
                betElement.textContent = player.bet > 0 ? `Bet: $${player.bet}` : '';

                // Add player cards
                const cardsElement = document.createElement('div');
                cardsElement.className = 'opponent-cards';

                player.cards.forEach(card => {
                    const cardElement = card.createCardElement();
                    cardsElement.appendChild(cardElement);
                });

                // Add status message if applicable
                let statusElement = null;
                if (player.folded) {
                    statusElement = document.createElement('div');
                    statusElement.className = 'player-status';
                    statusElement.textContent = 'FOLDED';
                } else if (player.isAllIn) {
                    statusElement = document.createElement('div');
                    statusElement.className = 'player-status all-in';
                    statusElement.textContent = 'ALL IN';
                }

                // Add hand description if at showdown
                let handElement = null;
                if (this.gameState.currentState === GameState.SHOWDOWN && !player.folded) {
                    handElement = document.createElement('div');
                    handElement.className = 'player-hand';
                    handElement.textContent = player.handDescription;
                }

                // Assemble the opponent element
                opponentElement.appendChild(nameElement);
                opponentElement.appendChild(chipsElement);
                opponentElement.appendChild(betElement);
                opponentElement.appendChild(cardsElement);

                if (statusElement) {
                    opponentElement.appendChild(statusElement);
                }

                if (handElement) {
                    opponentElement.appendChild(handElement);
                }

                this.opponentsContainer.appendChild(opponentElement);
            }
        });
    }

    /**
     * Update action buttons based on valid actions
     */
    updateActionButtons() {
        if (!this.gameState || !this.gameState.currentPlayer.isHuman) {
            // Disable all buttons if it's not the human player's turn
            this.disableAllActionButtons();
            return;
        }

        const player = this.gameState.currentPlayer;
        const currentBet = this.gameState.currentBet;
        const playerBet = player.bet;

        // Enable/disable fold button
        this.btnFold.disabled = false;

        // Enable/disable check button (can only check if no bet to call)
        this.btnCheck.disabled = currentBet > playerBet;

        // Enable/disable call button (can only call if there's a bet to match)
        this.btnCall.disabled = currentBet === playerBet;
        this.btnCall.textContent = `Call $${currentBet - playerBet}`;

        // Enable/disable bet button (can only bet if player has chips)
        this.btnBet.disabled = player.chips === 0;
        this.btnBet.textContent = currentBet > playerBet ? 'Raise' : 'Bet';
    }

    /**
     * Disable all action buttons
     */
    disableAllActionButtons() {
        this.btnFold.disabled = true;
        this.btnCheck.disabled = true;
        this.btnCall.disabled = true;
        this.btnBet.disabled = true;
    }

    /**
     * Handle the showdown
     */
    handleShowdown() {
        // Display all cards face up
        this.gameState.players.forEach(player => {
            if (!player.folded) {
                player.cards.forEach(card => {
                    card.faceUp = true;
                });
            }
        });

        // Update the UI to show all cards
        this.updatePlayerCards();
        this.updateOpponents();

        // Find winners
        const winners = this.game.determineWinners();

        if (winners.length > 0) {
            const winnerNames = winners.map(w => w.name).join(', ');
            this.showMessage(`Showdown! ${winnerNames} wins the pot of $${this.gameState.pot}!`);

            // Check if any winner is the human player
            if (winners.some(w => w.isHuman)) {
                this.showMessage('Congratulations! You won!', true);
            }
        } else {
            this.showMessage('No winners, pot is split.');
        }

        // Disable action buttons
        this.disableAllActionButtons();

        // Enable new game button
        this.btnNewGame.disabled = false;
    }

    /**
     * Display a message in the game message area
     * @param {string} message - The message to display
     * @param {boolean} important - Whether this is an important message
     */
    showMessage(message, important = false) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;

        if (important) {
            messageElement.classList.add('important');
        }

        this.gameMessages.innerHTML = '';
        this.gameMessages.appendChild(messageElement);
    }
}