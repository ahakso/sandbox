/**
 * Main entry point for the Texas Hold'em Poker game
 */

// Initialize the game UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create the UI controller
    const ui = new PokerUI();

    // Show welcome message
    ui.showMessage('Welcome to Texas Hold\'em Poker! Click "New Game" to start playing.', true);

    // Automatically start a new game
    setTimeout(() => {
        ui.startNewGame();
    }, 1000);
});

/**
 * Simple server to run the game on localhost
 * 
 * To start the server:
 * 1. Open a terminal in the project directory
 * 2. Run: node server.js
 * 3. Open your browser and navigate to: http://localhost:3000
 */