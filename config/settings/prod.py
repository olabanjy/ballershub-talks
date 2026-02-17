from .base import *


DEBUG = False

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ["64.23.147.193", "ballershub.talks.ng", "www.ballershub.talks.ng"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": "5432",
    }
}

STATIC_ROOT = "/home/devops/ballershub/static/"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

AUTO_MAIL_FROM = config("AUTO_MAIL_FROM", "dev@rainfall.ng")

EMAIL_SUBJECT_PREFIX = ["BallersHub Podcast"]

EMAIL_TIMEOUT = 360


DEFAULT_FROM_EMAIL = "dev@rainfall.ng"


EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")


ADMINS = (("BallersHub Podcast Support", "hello@zamari.tv"),)


# CELERY related settings
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Lagos"


DO_SPACES_ACCESS_KEY_ID = config("DO_SPACE_ACCESS_KEY")
DO_SPACES_SECRET_ACCESS_KEY = config("DO_SPACE_SECRET_KEY")
DO_SPACES_BUCKET_NAME = config("DO_SPACE_BUCKET_NAME")
DO_SPACES_REGION_NAME = "sfo3"
DO_SPACES_ENDPOINT_URL = "https://sfo3.digitaloceanspaces.com"


AWS_ACCESS_KEY_ID = DO_SPACES_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = DO_SPACES_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = DO_SPACES_BUCKET_NAME
AWS_S3_REGION_NAME = DO_SPACES_REGION_NAME
AWS_S3_ENDPOINT_URL = DO_SPACES_ENDPOINT_URL
AWS_S3_SIGNATURE_VERSION = "s3v4"


AWS_S3_CUSTOM_DOMAIN = (
    f"{DO_SPACES_BUCKET_NAME}.{DO_SPACES_REGION_NAME}.digitaloceanspaces.com"
)

AWS_DEFAULT_ACL = "public-read"

# Ensure file paths are correct
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

DEFAULT_FILE_STORAGE = "config.settings.storage_backends.MediaStorage"
