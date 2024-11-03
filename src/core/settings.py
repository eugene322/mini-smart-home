from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='core/.env',
        env_prefix='mini_home_'
    )

    bot_token: str

    redis_host: str
    redis_port: int
    redis_password: str

    mqtt_host: str
    mqtt_port: int
    mqtt_user: str
    mqtt_password: str
