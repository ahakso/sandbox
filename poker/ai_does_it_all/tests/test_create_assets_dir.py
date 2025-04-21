import os
import sys
import pytest
from unittest.mock import patch

# Add the parent directory to sys.path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import create_assets_dir


def test_assets_dir_creation():
    """Test that the assets directory is created correctly."""
    with patch("os.makedirs") as mock_makedirs:
        # Import the module to trigger the directory creation
        import importlib

        importlib.reload(create_assets_dir)

        # Check if os.makedirs was called with the correct arguments
        expected_dir = "/Users/ahakso/secondmeasure/data-tools/hakso/sandbox/poker_sandbox/assets/cards"
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)


def test_directory_exists():
    """Test that the assets directory exists after running the script."""
    expected_dir = "/Users/ahakso/secondmeasure/data-tools/hakso/sandbox/poker_sandbox/assets/cards"
    assert os.path.exists(expected_dir), f"Directory {expected_dir} was not created"
