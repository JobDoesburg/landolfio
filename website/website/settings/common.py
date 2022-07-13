"""The settings common to both development and production."""
import os
from pathlib import Path

from django.utils.translation import gettext_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Application definition

INSTALLED_APPS = [
    "website",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "admin_numeric_filter",
    "accounting",
    "inventory",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "website.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "website.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "nl"

TIME_ZONE = "Europe/Amsterdam"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (("nl", gettext_lazy("Dutch")),)

LOCALE_PATHS = [BASE_DIR / "locale/"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"


MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DJANGO_DRF_FILEPOND_UPLOAD_TMP = os.path.join(BASE_DIR, "filepond-temp-uploads")
# DJANGO_DRF_FILEPOND_FILE_STORE_PATH = os.path.join(BASE_DIR, "stored_uploads")
# DJANGO_DRF_FILEPOND_STORAGES_BACKEND = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_S3_REGION_NAME = 'eu-west-1'
# AWS_STORAGE_BUCKET_NAME = 'filepond-uploads'
# AWS_DEFAULT_ACL = 'private'
# AWS_BUCKET_ACL = 'private'
# AWS_AUTO_CREATE_BUCKET = True


# Moneybird resources to syncronize

MONEYBIRD_RESOURCE_TYPES = [
    "accounting.moneybird_resources.DocumentStyleResourceType",
    "accounting.moneybird_resources.TaxRateResourceType",
    "accounting.moneybird_resources.WorkflowResourceType",
    "accounting.moneybird_resources.LedgerAccountResourceType",
    "accounting.moneybird_resources.ProductResourceType",
    "accounting.moneybird_resources.ProjectResourceType",
    "accounting.moneybird_resources.ContactResourceType",
    "accounting.moneybird_resources.SalesInvoiceResourceType",
    "accounting.moneybird_resources.PurchaseInvoiceDocumentResourceType",
    "accounting.moneybird_resources.ReceiptResourceType",
    "accounting.moneybird_resources.GeneralJournalDocumentResourceType",
    "accounting.moneybird_resources.EstimateResourceType",
    "accounting.moneybird_resources.RecurringSalesInvoiceResourceType",
    "accounting.moneybird_resources.SubscriptionResourceType",
]
MONEYBIRD_WEBHOOK_SITE_DOMAIN = "http://localhost:8000"
MONEYBIRD_WEBHOOK_EVENTS = [
    "contact",
    "sales_invoice",
]
