from django.test import TestCase

from moneybird_accounting.models import Contact
from moneybird_accounting.moneybird_sync import MoneyBirdAPITalker


class MoneyBirdAPITalkerTest(TestCase):
    def setUp(self):
        self.mb = MoneyBirdAPITalker()

    def test_sync_contacts(self):
        """
        - No contacts, after sync there are
        - No updates, nothing touched
        - Remove contact from Django, reappears
        - Delete contact from Moneybird, disappears
        - Update contact, after synced change cascaded
        :return:
        """
        self.mb.sync_objects(Contact)

    # TODO write a lot of tests...
