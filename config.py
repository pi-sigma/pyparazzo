import os


class Config:
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    DEBUG = os.environ.get("DEBUG", True)

    # Secrets
    SECRET_KEY = os.environ.get("SECRET_KEY", "hush-hush")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL_FIXED", "sqlite:///blog.db"  # on heroku: "postgres" > "postgresql"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CKEDITOR_ENABLE_CODESNIPPET = True
