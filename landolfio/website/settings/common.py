"""The settings common to both development and production."""
import os
from pathlib import Path

from django.utils.translation import gettext_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from moneybird import webhooks
from moneybird.webhooks.events import WebhookEvent

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
    "django_countries",
    "django_easy_admin_object_actions",
    "localflavor",
    "admin_numeric_filter",
    "autocompletefilter",
    "django_drf_filepond",
    "ninox_import",
    "inventory",
    "accounting",
    "moneybird",
    "scantags",
    "bootstrap5",
    "rental_customers",
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

# LANGUAGE_CODE = "nl"

TIME_ZONE = "Europe/Amsterdam"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (("nl", gettext_lazy("Dutch")), ("en", gettext_lazy("English")))

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
MONEYBIRD_ADMINISTRATION_ID = int(os.environ.get("MONEYBIRD_ADMINISTRATION_ID", 0))
MONEYBIRD_API_KEY = os.environ.get("MONEYBIRD_API_KEY")
MONEYBIRD_RESOURCE_TYPES = [
    "accounting.models.document_style.DocumentStyleResourceType",
    "accounting.models.tax_rate.TaxRateResourceType",
    "accounting.models.workflow.WorkflowResourceType",
    "accounting.models.ledger_account.LedgerAccountResourceType",
    "accounting.models.product.ProductResourceType",
    "accounting.models.project.ProjectResourceType",
    "accounting.models.contact.ContactResourceType",
    "accounting.models.recurring_sales_invoice.RecurringSalesInvoiceResourceType",
    "accounting.models.estimate.EstimateResourceType",
    "accounting.models.sales_invoice.SalesInvoiceResourceType",
    "accounting.models.purchase_document.PurchaseInvoiceDocumentResourceType",
    "accounting.models.purchase_document.ReceiptResourceType",
    "accounting.models.general_journal_document.GeneralJournalDocumentResourceType",
    "accounting.models.subscription.SubscriptionResourceType",
]
MONEYBIRD_WEBHOOK_EVENTS = [
    WebhookEvent.CONTACT,
    WebhookEvent.SALES_INVOICE,
    WebhookEvent.DOCUMENT,
    WebhookEvent.ESTIMATE,
    WebhookEvent.RECURRING_SALES_INVOICE,
    WebhookEvent.SUBSCRIPTION_CANCELLED,
    WebhookEvent.SUBSCRIPTION_CREATED,
    WebhookEvent.SUBSCRIPTION_UPDATED,
    WebhookEvent.SUBSCRIPTION_EDITED,
    WebhookEvent.SUBSCRIPTION_DESTROYED,
    WebhookEvent.TAX_RATE_UPDATED,
    WebhookEvent.TAX_RATE_CREATED,
    WebhookEvent.TAX_RATE_DEACTIVATED,
    WebhookEvent.TAX_RATE_DESTROYED,
    WebhookEvent.TAX_RATE_ACTIVATED,
    WebhookEvent.WORKFLOW,
    WebhookEvent.LEDGER_ACCOUNT,
    WebhookEvent.PRODUCT_UPDATED,
    WebhookEvent.PRODUCT_CREATED,
    WebhookEvent.PRODUCT_DEACTIVATED,
    WebhookEvent.PRODUCT_DESTROYED,
    WebhookEvent.PRODUCT_ACTIVATED,
    WebhookEvent.PROJECT_UPDATED,
    WebhookEvent.PROJECT_CREATED,
    WebhookEvent.PROJECT_ARCHIVED,
    WebhookEvent.PROJECT_DESTROYED,
    WebhookEvent.PROJECT_ACTIVATED,
    WebhookEvent.DOCUMENT_STYLE_CREATED,
    WebhookEvent.DOCUMENT_STYLE_UPDATED,
    WebhookEvent.DOCUMENT_STYLE_DESTROYED,
]
MONEYBIRD_WEBHOOK_ID = os.environ.get("MONEYBIRD_WEBHOOK_ID")
MONEYBIRD_WEBHOOK_TOKEN = os.environ.get("MONEYBIRD_WEBHOOK_TOKEN")

MONEYBIRD_AUTO_PUSH = True
MONEYBIRD_FETCH_BEFORE_PUSH = False

NINOX_API_TOKEN = os.environ.get("NINOX_API_TOKEN")
NINOX_TEAM_ID = os.environ.get("NINOX_TEAM_ID")
NINOX_DATABASE_ID = os.environ.get("NINOX_DATABASE_ID")


AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_FILE_OVERWRITE = False
if AWS_STORAGE_BUCKET_NAME is not None:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DJANGO_DRF_FILEPOND_STORAGES_BACKEND = "storages.backends.s3boto3.S3Boto3Storage"
else:
    DJANGO_DRF_FILEPOND_STORAGES_BACKEND = "django.core.files.storage.FileSystemStorage"
    DJANGO_DRF_FILEPOND_FILE_STORE_PATH = os.path.join(MEDIA_ROOT, "stored_uploads")

DJANGO_DRF_FILEPOND_UPLOAD_TMP = os.path.join(MEDIA_ROOT, "filepond-temp-uploads")

NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "contact@vofdoesburg.nl")
