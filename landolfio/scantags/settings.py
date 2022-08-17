from django.conf import settings


def get(key, default):
    return getattr(settings, key, default)


SCANTAGS_ALPHABET = get("SCANTAGS_ALPHABET", "0123456789ACEFGHJKLMNPRTUWXYZ")
SCANTAGS_ID_LENGTH = get("SCANTAGS_ID_LENGTH", 8)
SCANTAGS_PREFIX = get("SCANTAGS_PREFIX", "A")

if len(SCANTAGS_PREFIX) > 1:
    for character in SCANTAGS_PREFIX:
        assert (
            character in SCANTAGS_ALPHABET
        ), "SCANTAGS_PREFIX must be in SCANTAGS_ALPHABET"
elif len(SCANTAGS_PREFIX) == 1:
    assert (
        SCANTAGS_PREFIX in SCANTAGS_ALPHABET
    ), "SCANTAGS_PREFIX must be in SCANTAGS_ALPHABET"
