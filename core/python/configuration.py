from pydantic.env_settings import BaseSettings
from sqlalchemy import create_engine


class Settings(BaseSettings):
    bot_name: str = ""
    bot_id: str = ""
    bot_alias_id: str = ""
    locale_Id: str = "en_GB"
    draft_version_name: str = "Draft version"

    database_name: str
    database_host: str
    database_username: str
    database_password: str


config = Settings()

engine = create_engine(
    f'postgresql://{config.database_username}:{config.database_password}@{config.database_host}/{config.database_name}',
    echo=True)
