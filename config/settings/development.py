from .base import *  # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Override with PostgreSQL if DATABASE_URL is set
import environ
env = environ.Env()
if env("DATABASE_URL", default=""):
    DATABASES["default"] = env.db("DATABASE_URL")

# SMTP is configured in base.py via .env (Gmail).
# Switch to console backend only if no password is set.
if not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use local memory cache in dev so Redis is optional
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

INTERNAL_IPS = ["127.0.0.1"]

# Relax axes in dev
AXES_ENABLED = False

# Ensure session cookie is set on the very first page-load (not just on first
# write). Without this, anonymous users get a new session on every AJAX request
# that hasn't been preceded by a page that set the cookie, causing the cart
# drawer to see a different (empty) cart than the one items were added to.
SESSION_SAVE_EVERY_REQUEST = True
