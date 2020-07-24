from django.apps import AppConfig


class AssetEventsConfig(AppConfig):
    name = "asset_events"
    verbose_name = "Asset events"

    def ready(self):
        from asset_events import signals  # noqa
