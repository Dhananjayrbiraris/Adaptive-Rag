"""
Configuration settings for the application.
Centralizes environment variables and YAML-based prompts.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables with validation."""

    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    TAVILY_API_KEY: str = Field(default="", description="Tavily search API key")
    QDRANT_URL: Optional[str] = Field(default=None, description="Qdrant vector database URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, description="Qdrant API key")
    CODE_COLLECTION: str = Field(default="codebase", description="Qdrant collection for code")
    DOCS_COLLECTION: str = Field(default="guidelines", description="Qdrant collection for docs")

    # MongoDB Configuration
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URL")
    MONGODB_DB_NAME: str = Field(default="adaptive_rag", description="MongoDB database name")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate_settings(self) -> bool:
        """Validate critical settings are configured."""
        if not self.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not configured")
            return False
        if not self.QDRANT_URL:
            logger.error("QDRANT_URL is not configured")
            return False
        return True


class PromptConfig:
    """Load and manage configuration from YAML file."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration from YAML file.

        Args:
            config_file: Optional path to config file. Defaults to prompts.yaml.
        """
        base_path = Path(__file__).parent
        config_path = (
            base_path / "prompts.yaml"
            if config_file is None
            else Path(config_file)
        )
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        if "prompts" not in self.config:
            raise ValueError("Invalid config format: 'prompts' key missing")

    def prompt(self, key: str) -> str:
        """
        Retrieve a prompt from configuration.

        Args:
            key: The prompt key.

        Returns:
            The prompt template string.
            
        Raises:
            KeyError: If prompt key doesn't exist.
        """
        try:
            return self.config["prompts"][key]
        except KeyError:
            logger.error(f"Prompt key '{key}' not found in configuration")
            raise


# Global instances
try:
    settings = Settings()
    if not settings.validate_settings():
        logger.warning("Some settings are not properly configured")
except ValidationError as e:
    logger.error(f"Settings validation failed: {e}")
    raise

prompt_config = PromptConfig()

# Set env variables for LangChain integrations
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
