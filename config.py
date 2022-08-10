import os


class Basic:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CKEDITOR_ENABLE_CODESNIPPET = True


class Dev(Basic):
    SECRET_KEY = "hush-hush"

    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"


class Prod(Basic):
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL_FIXED", "sqlite:///blog.db"  # on heroku: "postgres" > "postgresql"
    )
