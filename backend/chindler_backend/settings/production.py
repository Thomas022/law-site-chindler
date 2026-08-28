import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


required_variables = [
    "DJANGO_SECRET_KEY",
    "DATABASE_URL",
    "CLOUDINARY_URL",
]
render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)  # noqa: F405
elif not os.environ.get("DJANGO_ALLOWED_HOSTS"):
    required_variables.append("DJANGO_ALLOWED_HOSTS")
missing_variables = [name for name in required_variables if not os.environ.get(name)]
if missing_variables:
    raise ImproperlyConfigured(
        "Variáveis obrigatórias ausentes: " + ", ".join(missing_variables)
    )

DEBUG = False
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "true").lower() == "true"
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Render captures stdout/stderr. Keep request bodies and credentials out of the
# format while preserving exception tracebacks needed to diagnose HTTP 500s.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "production",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
