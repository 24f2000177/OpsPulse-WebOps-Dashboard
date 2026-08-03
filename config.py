import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "opspulse-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" +
        os.path.join(
            BASE_DIR,
            "instance",
            "opspulse.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT = False

    SESSION_TYPE = "filesystem"

    JSON_SORT_KEYS = False

    TEMPLATES_AUTO_RELOAD = True