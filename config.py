import os
from dotenv import load_dotenv

# Muat environment variable dari file .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Konfigurasi Aplikasi Flask & Database MySQL"""
    SECRET_KEY = os.getenv("SECRET_KEY", "kunci-rahasia-samsat-medan-selatan-default")

    # Konfigurasi Koneksi MySQL (Default XAMPP: user=root, password kosong)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "db_fiskal_samsat")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi Upload Berkas
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "documents")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
