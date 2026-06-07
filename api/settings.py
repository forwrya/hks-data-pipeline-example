from pydantic import Field
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    db_connection_string: str = Field(default="", alias="DB_CONNECTION_STRING")
    environment: str = Field(default="local", alias="ENVIRONMENT")