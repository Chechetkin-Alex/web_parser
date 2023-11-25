from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    yandex_trains_api_key: SecretStr
    yandex_weather_api_key: SecretStr
    telegram_api_token: SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
