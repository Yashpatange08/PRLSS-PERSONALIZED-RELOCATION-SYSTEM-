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

# ── Cache / Redis ─────────────────────────────────────────────────────────────
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"socket_connect_timeout": 5, "socket_timeout": 5},
        "TIMEOUT": 300,
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
STATICFILES_DIRS = [BASE_DIR / "static"]
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
GOOGLE_MAPS_API_KEY  = os.environ.get("AIzaSyBaJ7dwqIKrNMkGU0rzAmz5773PQeyUXcE", "")
GOOGLE_PLACES_API_KEY = "AIzaSyBaJ7dwqIKrNMkGU0rzAmz5773PQeyUXcE"
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

# ── Multi-city config ─────────────────────────────────────────────────────────
CITY_CONFIG = {
    "nashik": {
        "name": "Nashik",
        "center_lat": 19.9975,
        "center_lon": 73.7898,
        "max_rent": 25000,
        "currency": "₹",
        "emoji": "🏙️",
        "popular_areas": [
            "College Road, Nashik",
            "CBS Road, Nashik",
            "Gangapur Road, Nashik",
            "CIDCO, Nashik",
            "Panchavati, Nashik",
        ],
    },
    "mumbai": {
        "name": "Mumbai",
        "center_lat": 19.0760,
        "center_lon": 72.8777,
        "max_rent": 80000,
        "currency": "₹",
        "emoji": "🌆",
        "popular_areas": [
            "Andheri West, Mumbai",
            "Bandra, Mumbai",
            "Powai, Mumbai",
            "Thane, Mumbai",
            "Borivali, Mumbai",
        ],
    },
    "pune": {
        "name": "Pune",
        "center_lat": 18.5204,
        "center_lon": 73.8567,
        "max_rent": 50000,
        "currency": "₹",
        "emoji": "🏘️",
        "popular_areas": [
            "Hadapsar, Pune",
            "Hinjewadi, Pune",
            "Kothrud, Pune",
            "Viman Nagar, Pune",
            "Wakad, Pune",
            "Baner, Pune",
        ],
    },
}

DEFAULT_CITY        = "nashik"
SEARCH_RADIUS_KM    = 5.0
MAX_RECOMMENDATIONS = 5

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
