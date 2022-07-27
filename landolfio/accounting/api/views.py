"""The views of the accounting app API."""
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse

from accounting.services import sync_moneybird


@login_required
def sync_database_hook(_request: HttpRequest) -> HttpResponse:
    """
    Synchronize the database.

    When a request to this hook occurs, the database will be synchronized from the
    remote MoneyBird administration.
    """
    sync_moneybird()
    return HttpResponse("The database was successfully updated.")