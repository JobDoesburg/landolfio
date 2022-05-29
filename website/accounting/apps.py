"""The Django apps concerning accounting."""
import os
import signal
import sys
from datetime import timedelta

from django.apps import AppConfig
from django.conf import settings
from timeloop import Timeloop

tl = Timeloop()


def shutdown(*args):
    """Shutdown the timeloop."""
    if os.environ.get("RUN_MAIN", None) != "true":
        tl.stop()
    sys.exit(0)


@tl.job(interval=timedelta(minutes=settings.MONEYBIRD_SYNC_INTERVAL))
def update_database():
    """Update the database in the background."""
    # pylint: disable=import-outside-toplevel
    # We can only import here as the other models are not loaded yet when this file
    # is initialized
    from .sync_database import sync_database

    sync_database()


class AccountingConfig(AppConfig):
    """Accounting app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounting"

    def ready(self):
        """Start the timeloop if this is called on the main thread."""
        # The ready function is called twice if `runserver` is used:
        # Once for the actual application and once to automatically reload the
        #   application if changes are detected
        # This check assures that the time loop is only started once
        if os.environ.get("RUN_MAIN", None) != "true":
            tl.start()
            signal.signal(signal.SIGINT, shutdown)
