from django.apps import AppConfig

# TODO better document everything


class MoneybirdAccountingConfig(AppConfig):
    name = "moneybird_accounting"
    label = "moneybird"
    verbose_name = "Moneybird"

    def ready(self):
        from moneybird_accounting import signals  # noqa
