import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "3306")
    db_name: str = os.getenv("DB_NAME", "fast_api")
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent
    
    @property
    def storage_dir(self) -> Path:
        return self.base_dir / "storage"
    
    @property
    def docs_dir(self) -> Path:
        return self.storage_dir / "docs"

    @property
    def cv_dir(self) -> Path:
        return self.storage_dir / "cv"
    
    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / "uploads"
    
    @property
    def temp_dir(self) -> Path:
        return self.storage_dir / "temp"
    
    @property
    def images_dir(self) -> Path:
        return self.storage_dir / "images"


settings = Settings()
