import os
import logging
from stockfish import Stockfish

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def show_board(stockfish):
    print(stockfish.get_board_visual())


def initialize_stockfish():
    stockfish_path = "/opt/homebrew/bin/stockfish"
    logger.debug(f"Using Stockfish at: {stockfish_path}")
    logger.debug(f"Stockfish exists: {os.path.exists(stockfish_path)}")
    logger.debug(f"Stockfish is executable: {os.access(stockfish_path, os.X_OK)}")

    # Initialize Stockfish
    try:
        stockfish = Stockfish(
            path=stockfish_path,
            depth=15,
            parameters={
                "Debug Log File": "",
                "Contempt": 0,
                "Min Split Depth": 0,
                "Threads": 1, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
                "Ponder": "false",
                "Hash": 32, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
                "MultiPV": 1,
                "Skill Level": 20,
                "Move Overhead": 10,
                "Minimum Thinking Time": 20,
                "Slow Mover": 100,
                "UCI_Chess960": "false",
                "UCI_LimitStrength": "false"
            }
        )
        logger.debug("Stockfish initialized successfully")
        stockfish.set_elo_rating(1350)
        logger.debug("Stockfish ELO set")
        initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        stockfish.set_fen_position(initial_fen)
        logger.debug("Stockfish initial position set")
        show_board(stockfish)

        if stockfish.is_move_correct("d2d5"):
            print("YES")
        else:
            print("NO")

        stockfish.make_moves_from_current_position(["e2e4"])
        show_board(stockfish)

        return stockfish
    except Exception as e:
        logger.error(f"Error initializing Stockfish: {e}")
        raise

if __name__ == "__main__":
    stockfish = initialize_stockfish()
