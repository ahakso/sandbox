import os

# Create assets directory if it doesn't exist
assets_dir = "/Users/ahakso/secondmeasure/data-tools/hakso/sandbox/poker_sandbox/assets/cards"
os.makedirs(assets_dir, exist_ok=True)
print(f"Created assets directory at: {assets_dir}")
