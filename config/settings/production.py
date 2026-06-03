from .base import *  # noqa
import environ

env = environ.Env()

DATABASES = {"default": env.db("DATABASE_URL")}

# ALLOWED_HOSTS: always include the Render subdomain automatically,
# plus whatever is set in the ALLOWED_HOSTS env var (e.g. custom domain).
import os
_render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")  # set by Render automatically
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
if _render_hostname and _render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_hostname)

# CSRF must also trust the Render domain
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h]

# Render terminates SSL at the load balancer — trust X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session must persist between AJAX requests (cart fix)
SESSION_SAVE_EVERY_REQUEST = True

# Axes is fine in production but allow all IPs (Render uses dynamic IPs)
AXES_ENABLED = True

# S3 media storage (optional — set AWS vars in Render env to enable)
if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

# Email — Gmail SMTP (same as dev, credentials come from env vars)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="wonzayskollections@gmail.com")
