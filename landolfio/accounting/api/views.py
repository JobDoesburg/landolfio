from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from accounting.services import sync_moneybird


@login_required
def sync_database_hook(_request: HttpRequest) -> HttpResponse:
    sync_moneybird()
    return HttpResponse(_("The database was successfully updated."))
