# Texas Hold'em Game - Manual Test Steps

## Basic Game Flow Test

1. **Start the game**:
   ```
   python main.py
   ```
   Choose your preferred interface (CLI or GUI).

2. **Pre-flop phase**:
   - Verify you can see your hand (2 cards)
   - Verify no community cards are shown
   - Verify you can make betting decisions (fold/call/check/raise)
   - Choose an action and verify your chips change accordingly

3. **Flop phase**:
   - Verify 3 community cards appear
   - Verify you can make betting decisions
   - Choose an action and verify your chips change accordingly

4. **Turn phase**:
   - Verify a 4th community card appears
   - Verify you can make betting decisions
   - Choose an action and verify your chips change accordingly

5. **River phase**:
   - Verify a 5th community card appears
   - Verify you can make betting decisions
   - Choose an action and verify your chips change accordingly

6. **Hand completion**:
   - Verify the winner is determined
   - Verify chips are awarded to the winner
   - Verify you can start a new hand

## Additional Tests

### Folding Test
1. Start a new hand
2. Choose to fold
3. Verify the game continues without you
4. Verify you can start a new hand afterward

### All-in Test
1. Start with a small number of chips
2. Make a large raise or call
3. Verify you go all-in correctly

### Bot Decision Test
1. Play multiple hands
2. Observe bot decisions
3. Verify bots make different decisions based on their cards and the stage

## How to Run Automated Tests

```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m unittest test_game.py
```
