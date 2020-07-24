from django.apps import AppConfig


class AssetsConfig(AppConfig):
    name = "assets"

    def ready(self):
        from assets import signals  # noqa
