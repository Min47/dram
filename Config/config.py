from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "config.env"))

class PostgresConfig:
    # Neon Postgres database configuration
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_conn = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=require&channel_binding=require"

    @classmethod
    def connection_url(cls):
        return f"postgresql://{cls.db_user}:{cls.db_password}@{cls.db_host}/{cls.db_name}?sslmode=require&channel_binding=require"
    
class Config:
    postgres = PostgresConfig