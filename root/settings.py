import datetime
from pathlib import Path
import environ

""" APPLICATION CONFIGURATIONS """

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = True
SECRET_KEY = env("SECRET_KEY")
ENVIRONMENT = env("ENVIRONMENT")
SITE_ID = int(env("SITE_ID"))

DOMAIN = env("DOMAIN")
PROTOCOL = env("PROTOCOL")
BASE_URL = f"{PROTOCOL}://{DOMAIN}"
# ALLOWED_HOSTS = str(env('ALLOWED_HOSTS')).split(',')
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [f"{PROTOCOL}://{host}" for host in ALLOWED_HOSTS]
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "dashboard:index"
GOOGLE_CALLBACK_ADDRESS = f"{BASE_URL}/accounts/google/login/callback/"
APPLE_CALLBACK_ADDRESS = f"{BASE_URL}/accounts/apple/login/callback/"

ROOT_URLCONF = "root.urls"
AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"


INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # STARTERS
    "crispy_forms",
    "crispy_bootstrap4",
    # YOUR APPS
    "phonenumber_field",
    "src.web.accounts",
    "src.web.dashboard",
    "src.services.invoice",
    "src.services.customer",
    "src.services.project",
    "src.services.quotation",
    "src.services.loan",
    "src.services.expense",
    "src.services.assets",
    "src.services.transaction",
    "src.services.vendor",
    "src.services.charts",
    "src.core",
]
# MAILCHIMP SETTINGS
MAILCHIMP_API_KEY = env("MAILCHIMP_API_KEY")
MAILCHIMP_FROM_EMAIL = env("MAILCHIMP_FROM_EMAIL")
EMAIL_HOST = "smtp.mandrillapp.com"

# GOOGLE SETTINGS
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_PORT = "587"
EMAIL_HOST = "smtp.gmail.com"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# PHONE NUMBER SETTINGS
PHONENUMBER_DEFAULT_REGION = "PK"
PHONENUMBER_DEFAULT_FORMAT = "NATIONAL"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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
            ],
        },
    },
]

WSGI_APPLICATION = "root.wsgi.application"


if ENVIRONMENT == "server":
    print("server")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "myproject",
            "USER": "myprojectuser",
            "PASSWORD": "password",
            "HOST": "localhost",
            "PORT": "",
        }
    }

else:
    print("local")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

""" INTERNATIONALIZATION --------------------------------------------------------------------------------"""
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_L10N = True
USE_TZ = True

""" EMAIL CONFIGURATION --------------------------------------------------------------------------------"""
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "assets"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

""" RESIZER IMAGE --------------------------------------------------------------------------------"""
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = "JPEG"
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".gif"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

""" ALL-AUTH SETUP --------------------------------------------------------------------------------"""
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_EMAIL_VERIFICATION = "none"

""" MFA SETUP --------------------------------------------------------------------------------"""
MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"

"""  ACCOUNT ADAPTER Modify Login/Signup Redirect UR----------------------------------------------------"""
ACCOUNT_ADAPTER = "src.web.accounts.adapters.MyAccountAdapter"
