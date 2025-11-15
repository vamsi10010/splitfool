"""Entry point for Splitfool application."""

import argparse
import sys

from splitfool.config import Config
from splitfool.ui.app import SplitfoolApp


def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Splitfool - Bill Splitting TUI Application")
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to SQLite database file (default: ./splitfool.db)",
    )
    
    args = parser.parse_args()
    
    # Create config
    config = Config(db_path=args.db_path)
    
    # Run application
    app = SplitfoolApp(config=config)
    app.run()


if __name__ == "__main__":
    sys.exit(main())
