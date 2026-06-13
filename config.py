"""Configuration management for MIGO."""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Application configuration."""

    # Arena PLM Configuration
    ARENA_API_KEY: str = os.getenv("ARENA_API_KEY", "")
    ARENA_API_URL: str = os.getenv(
        "ARENA_API_URL", "https://api.arenasolutions.com/v1"
    )
    ARENA_TIMEOUT: int = int(os.getenv("ARENA_TIMEOUT", "30"))

    # Claude Configuration
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "2048"))

    # Report Configuration
    REPORT_FORMAT: str = os.getenv("REPORT_FORMAT", "table")  # table, csv, json
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./reports")

    # Validation Configuration
    REQUIRED_FIELDS: list = [
        "sku",
        "name",
        "category",
        "status",
    ]

    MATERIAL_FIELD_REGEX: dict = {
        "material_code": r"^[A-Z0-9]{3,10}$",
        "material_grade": r"^[A-Z0-9]{2,8}$",
    }

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configurations are set."""
        if not cls.ARENA_API_KEY:
            raise ValueError("ARENA_API_KEY not configured")
        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY not configured")
        return True


if __name__ == "__main__":
    print("Configuration loaded successfully.")
    print(f"Arena API URL: {Config.ARENA_API_URL}")
    print(f"Claude Model: {Config.CLAUDE_MODEL}")
