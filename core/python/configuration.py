from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    bot_name: str = ""
    bot_id: str = ""
    bot_alias_id: str = ""
    locale_Id: str = "en_GB"
    draft_version_name: str = "Draft version"


config = Settings()
