"""
The MoneyBird API.

This code is largely based on moneybird-python by Jan-Jelle Kester,
licensed under the MIT license. The source code of moneybird-python
can be found on GitHub: https://github.com/jjkester/moneybird-python.
"""
from abc import ABC
from abc import abstractmethod
from functools import reduce
from typing import Type
from urllib.parse import urljoin

import requests


class Administration(ABC):
    """A MoneyBird administration."""

    @abstractmethod
    def get(self, resource_path: str):
        """Do a GET on the Moneybird administration."""

    @abstractmethod
    def post(self, resource_path: str, data: dict):
        """Do a POST request on the Moneybird administration."""

    class InvalidResourcePath(Exception):
        """The given resource path is invalid."""

    class Error(Exception):
        """An exception that can be thrown while using the administration."""

        def __init__(self, status_code: int, description: str = None):
            """Create a new administration error."""
            msg = f"API error {status_code}"
            if description:
                msg += f": {description}"

            super().__init__(msg)

    class Unauthorized(Error):
        """The client has insufficient authorization."""

    class NotFound(Error):
        """The client requested a resource that could not be found."""

    class InvalidData(Error):
        """The client sent invalid data."""

    class Throttled(Error):
        """The client sent too many requests."""

    class ServerError(Error):
        """An error happened on the server."""


def _create_session_with_key(key: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {key}"})
    return session


def _build_url(administration_id: int, resource_path: str) -> str:
    if resource_path.startswith("/"):
        raise Administration.InvalidResourcePath(
            "The resource path must not start with a slash."
        )

    api_base_url = "https://moneybird.com/api/v2/"
    url_parts = [api_base_url, f"{administration_id}/", f"{resource_path}.json"]
    return reduce(urljoin, url_parts)


def _process_response(response: requests.Response) -> dict:
    good_codes = {200, 201, 204}
    bad_codes: dict[int, Type[Administration.Error]] = {
        400: Administration.Unauthorized,
        401: Administration.Unauthorized,
        403: Administration.Throttled,
        404: Administration.NotFound,
        406: Administration.NotFound,
        422: Administration.InvalidData,
        429: Administration.Throttled,
        500: Administration.ServerError,
    }

    code = response.status_code

    # pylint: disable=consider-iterating-dictionary
    code_is_known: bool = code in good_codes | bad_codes.keys()

    if not code_is_known:
        raise Administration.Error(code, "API response contained unknown status code")

    if code in bad_codes:
        error = bad_codes[code]
        try:
            error_description = response.json()["error"]
        except (AttributeError, TypeError, KeyError, ValueError):
            error_description = None

        raise error(code, error_description)

    return response.json()


class HttpsAdministration(Administration):
    """The HTTPS implementation of the MoneyBird Administration interface."""

    def __init__(self, key, administration_id: int):
        """Create a new MoneyBird administration connection."""
        super().__init__()
        self.session = _create_session_with_key(key)
        self.administration_id = administration_id

    def post(self, resource_path: str, data: dict):
        """Do a POST request on the Moneybird administration."""
        url = _build_url(self.administration_id, resource_path)
        response = self.session.post(url, json=data)
        return _process_response(response)

    def get(self, resource_path: str):
        """Do a GET on the Moneybird administration."""
        url = _build_url(self.administration_id, resource_path)
        response = self.session.get(url)
        return _process_response(response)


class MockAdministration(Administration):
    """Mock version of a MoneyBird administration."""

    def __init__(self, documents: dict[str, list[dict]]):
        """Initialize a new MockAdministration."""
        super().__init__()
        self.documents = documents

    def get(self, resource_path: str):
        """Mock a GET request for the Moneybird Administration."""
        parts = resource_path.split("/")

        # Mock a GET request for a /documents/* resource path
        if (
            len(parts) == 3
            and parts[0] == "documents"
            and parts[2] == "synchronization"
        ):
            documents_kind = (
                self.documents[parts[1]] if parts[1] in self.documents else [].copy()
            )

            return [
                {"id": doc["id"], "version": doc["version"]} for doc in documents_kind
            ]

        raise self.NotFound

    def post(self, resource_path: str, data: dict):
        """Mock a POST request for the Moneybird Administration."""
        path = resource_path.split("/")
        if len(path) == 3 and path[0] == "documents" and path[2] == "synchronization":
            if path[1] in self.documents:
                documents_kind = self.documents[path[1]]
            else:
                documents_kind = [].copy()

            ids = data["ids"]
            return filter(lambda doc: doc["id"] in ids, documents_kind)

        # Incorrect path was used
        raise self.NotFound