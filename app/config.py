from functools import lru_cache
import os

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = "sqlite:///./data/searcher.db"
    bing_search_url: str = "https://www.bing.com/search"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data/searcher.db"),
        bing_search_url=os.getenv("BING_SEARCH_URL", "https://www.bing.com/search"),
    )
