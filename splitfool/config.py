"""Configuration management for Splitfool application."""

from pathlib import Path


class Config:
    """Application configuration."""

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize configuration.

        Args:
            db_path: Optional custom database path
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.cwd() / "splitfool.db"

    @property
    def db_path_str(self) -> str:
        """Get database path as string.

        Returns:
            Database path as string
        """
        return str(self.db_path)


# Default configuration instance
default_config = Config()
