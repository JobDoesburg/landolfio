from django.conf import settings

from .moneybird import Administration
from .moneybird import HttpsAdministration


def _update_database_from_api(_api: Administration) -> None:
    # pylint: disable=fixme
    # TODO: implement
    pass


def update_database() -> None:
    administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
    key = settings.MONEYBIRD_API_KEY
    administration = HttpsAdministration(key, administration_id)

    _update_database_from_api(administration)
