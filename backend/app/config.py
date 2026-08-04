import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Upload settings
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_SIZE_MB = 500

# JWT Auth settings
SECRET_KEY = os.getenv("DATAPURIFY_SECRET_KEY", "dev-secret-key-change-in-production-!@#$%")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# CORS origins (update for deployment)
CORS_ORIGINS = os.getenv("DATAPURIFY_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
