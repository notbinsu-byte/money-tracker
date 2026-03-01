from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Money Tracker"
    DATABASE_URL: str = "sqlite:///./money_tracker.db"
    BASE_CURRENCY: str = "USD"
    CURRENCY_API_URL: str = "https://api.frankfurter.app"
    ITEMS_PER_PAGE: int = 20

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
