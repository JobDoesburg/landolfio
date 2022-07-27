"""The views for the main Landolfio app."""
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse


@login_required
def protected_ask_reverse_proxy(request: HttpRequest):
    """
    If the user is authenticated, ask the reverse proxy to serve the requested file.

    If the user is not authenticated, then redirect to the login page.

    This is done through the X-Accel-Redirect header.

    """
    # Ask the reverse proxy to serve the requested file.
    response = HttpResponse(status=200, content_type="")
    response.headers["X-Accel-Redirect"] = request.path
    return response
