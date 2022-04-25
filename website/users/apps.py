"""The Django apps concerning users."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """User app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
