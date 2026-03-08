from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Money Tracker"
    DATABASE_URL: str = "sqlite:///./money_tracker.db"
    BASE_CURRENCY: str = "USD"
    CURRENCY_API_URL: str = "https://api.frankfurter.app"
    ITEMS_PER_PAGE: int = 20
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = ""
    ANTHROPIC_AUTH_TOKEN: str = ""
    ANTHROPIC_MODEL: str = "claude-opus-4-6-20250219"

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
