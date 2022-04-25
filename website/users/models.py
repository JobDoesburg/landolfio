"""The user models."""
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user class that inherits the AbstractUser class."""

    def __init__(self, *args, **kwargs):
        """
        Initialize the user model.

        Makes sure that the created users have staff and superuser permissions
        by default on creation.
        """
        self._meta.get_field("is_superuser").default = True
        self._meta.get_field("is_staff").default = True
        super().__init__(*args, **kwargs)
