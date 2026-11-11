"""Local development: SQLite and debug mode."""

from config.settings.base import *  # noqa: F401, F403
from config.settings.base import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
