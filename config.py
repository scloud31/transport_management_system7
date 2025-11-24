import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'transport-system-secret-key-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///transport_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'storage'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB