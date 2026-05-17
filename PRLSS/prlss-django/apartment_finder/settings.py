"""
Django Settings for PRLSS
Full production-ready config with PostgreSQL, Redis,
Google Maps API, CORS for React frontend, multi-city support.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-prlss-change-in-production-abc123xyz"
)
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0"
).split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "recommender",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "apartment_finder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "recommender.context_processors.google_maps_key",
            ],
        },
    },
]

WSGI_APPLICATION = "apartment_finder.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
_DB_URL = os.environ.get("DATABASE_URL", "")
if _DB_URL.startswith("postgres"):
    import dj_database_url
    DATABASES = {"default": dj_database_url.config(default=_DB_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Cache ─────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "prlss-cache",
    }
}

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "60/minute",
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "EXCEPTION_HANDLER": "recommender.utils.custom_exception_handler",
}

# ── CORS — allow React dev server (localhost:5173) ────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",   # fallback CRA port
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

# ── Static / Media ────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
_STATIC_DIR = BASE_DIR / "static"
STATICFILES_DIRS = [_STATIC_DIR] if _STATIC_DIR.exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Google Maps ───────────────────────────────────────────────────────────────
GOOGLE_MAPS_API_KEY  = os.environ.get("GOOGLE_MAPS_API_KEY", "AIzaSyC9YS3Kn3RwLkg6BzKyFFABRNmE4uVT3W0")
GOOGLE_PLACES_API_KEY = GOOGLE_MAPS_API_KEY
GEOCODING_REGION     = "IN"
GEOCODING_LANGUAGE   = "en"

CITY_BOUNDS = {
    "nashik": {"sw": {"lat": 19.85, "lng": 73.65}, "ne": {"lat": 20.15, "lng": 74.00}},
    "pune":   {"sw": {"lat": 18.35, "lng": 73.70}, "ne": {"lat": 18.70, "lng": 74.00}},
    "mumbai": {"sw": {"lat": 18.85, "lng": 72.75}, "ne": {"lat": 19.30, "lng": 73.00}},
}

# ── ML Paths ──────────────────────────────────────────────────────────────────
ML_MODEL_PATH       = BASE_DIR / "data" / "apartment_model.pkl"
TIMELINE_CSV_PATH   = BASE_DIR / "data" / "extracted_timeline.csv"
APARTMENTS_CSV_PATH = BASE_DIR / "data" / "ml_apartments.csv"

# ── City config — cities are now stored in the City DB table ─────────────────
# Loaded via: python manage.py import_cities
# No longer hardcoded. Supports all 157+ Indian cities.
# DEFAULT_CITY is used as fallback for geocoding when no city is selected.
DEFAULT_CITY        = "nashik"
SEARCH_RADIUS_KM    = 5.0
MAX_RECOMMENDATIONS = 5

# Default max rent used when city not found in DB
DEFAULT_MAX_RENT = 50000

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "recommender": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
