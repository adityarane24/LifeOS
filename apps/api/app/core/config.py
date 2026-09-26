# This file contains application configuration.
#
# Later, values such as database passwords and API keys
# will come from environment variables rather than being
# written directly into our source code.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    Pydantic reads these values from environment variables
    when we configure the application.
    """

    # Name of our application.
    app_name: str = "LifeOS"

    # Current API version.
    app_version: str = "0.1.0"

    # Database connection URL.
    #
    # We are temporarily giving it a local development
    # value. We will move this into .env shortly.
    database_url: str = (
        "postgresql+psycopg://"
        "lifeos:lifeos_dev_password@"
        "localhost:5432/lifeos"
    )


# Create one settings object that the rest of the
# application can import and use.
settings = Settings()