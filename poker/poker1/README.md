# Texas Hold'em Poker Game

A simple Texas Hold'em poker game where you can play against two bots.

## Features

- Play Texas Hold'em poker against two AI opponents
- Choose between text-based CLI or graphical window interface
- Proper poker hand evaluation
- Betting, raising, calling, checking, folding
- Blinds and dealer rotation
- Chip tracking

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd poker_sandbox
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## How to Run

Run the main script and choose your preferred interface:

```
python main.py
```

### Interface Options

1. **Text-based CLI** - Works in any terminal, no additional dependencies
2. **Graphical Window** - Uses pygame for a visual experience

## Controls

### CLI Version
- Follow the text prompts to play
- Type commands like "check", "call", "raise", or "fold"

### GUI Version
- Click on buttons to perform actions
- Cards are displayed visually on the poker table
- Your cards are shown at the bottom, bot cards at the top

## Game Rules

Standard Texas Hold'em rules:
- Each player is dealt 2 private cards
- 5 community cards are revealed in stages: flop (3 cards), turn (1 card), river (1 card)
- Betting rounds between each stage
- Best 5-card hand wins

Enjoy playing!
