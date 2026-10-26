"""Application settings and environment variable management."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Determine the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRETS_DIR = BASE_DIR / "secrets"

# Load environment variables from .env file
load_dotenv(dotenv_path=SECRETS_DIR / ".env")


class OdooSettings(BaseModel):
    """Configuration settings for Odoo XML-RPC connection."""

    url: str = Field(
        default_factory=lambda: os.getenv("ODOO_URL", "http://localhost:8069")
    )
    db: str = Field(default_factory=lambda: os.getenv("ODOO_DB", "odoo_db"))
    username: str = Field(default_factory=lambda: os.getenv("ODOO_USERNAME", "admin"))
    password: str = Field(default_factory=lambda: os.getenv("ODOO_PASSWORD", "admin"))
    timeout: int = Field(default_factory=lambda: int(os.getenv("ODOO_TIMEOUT", "10")))


settings = OdooSettings()
