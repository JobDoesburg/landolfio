"""The Django apps concerning accounting."""
import os
import threading
from threading import Event

from django.apps import AppConfig
from django.conf import settings

from .moneybird.administration import Administration

shutting_down = Event()


def _detect_shutdown():
    main_thread = threading.main_thread()
    main_thread.join()
    shutting_down.set()


def _update_database():
    """Update the database in the background."""
    # pylint: disable=import-outside-toplevel
    # We can only import here as the other models are not loaded yet when this file
    # is initialized
    from .sync_database import sync_database

    shutting_down.wait(10)

    while not shutting_down.is_set():
        try:
            sync_database()
            print("The database was successfully updated")
        except Administration.Error as error:
            print("Something went wrong while trying to update the database")
            print(error)
        finally:
            shutting_down.wait(settings.MONEYBIRD_SYNC_INTERVAL * 60)

    print("Update database thread was successfully shut down")


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
            update_database_thread = threading.Thread(
                target=_update_database, daemon=False
            )
            update_database_thread.start()

            watcher = threading.Thread(target=_detect_shutdown, daemon=False)
            watcher.start()
