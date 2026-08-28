"""Regression test: admin media must render with a CSP nonce (Django 6.1+)."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase


class AdminMediaNonceTest(TestCase):
    """All registered admins must render their media with a CSP nonce.

    Media paths added as raw strings to Media internals (as
    django-autocompletefilter did) lack __html__ and crash Django 6.1's
    CSP nonce rendering.
    """

    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.user = get_user_model()(
            is_superuser=True, is_staff=True, is_active=True
        )

    def test_all_admin_media_renders_with_nonce(self):
        for model, model_admin in admin.site._registry.items():
            with self.subTest(model=model.__name__):
                model_admin.media.render(attrs={"nonce": "test"})
                form = model_admin.get_form(self.request)()
                (model_admin.media + form.media).render(attrs={"nonce": "test"})
                for inline in model_admin.get_inline_instances(self.request):
                    formset = inline.get_formset(self.request)()
                    (inline.media + formset.media).render(attrs={"nonce": "test"})
