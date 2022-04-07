"""
A custom Django Test Runner.

The custom test runner is based on a Stack Overflow answer by meshy:
https://stackoverflow.com/a/17066553/. That answer is licensed under the Creative
Commons Attribution-ShareAlike 3.0 Unported license, which can be found here:
https://creativecommons.org/licenses/by-sa/3.0/.
"""
from django.conf import settings
from django.test.runner import DiscoverRunner


class TestRunner(DiscoverRunner):
    """A custom Django Test Runner, extending the existing DiscoverRunner."""

    def setup_test_environment(self, **kwargs):
        """
        Set up the environment for testing.

        Specifically, use an in memory storage.
        """
        super().setup_test_environment(**kwargs)

        # Use the in memory storage, for better test isolation and faster tests.
        settings.DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"
