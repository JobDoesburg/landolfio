from django.contrib import admin
from django.shortcuts import redirect
from django_easy_admin_object_actions.admin import ObjectActionsMixin
from django.utils.translation import gettext_lazy as _
from django_easy_admin_object_actions.decorators import object_action

from rental_customers.models import RegisteredRentalCustomer
from rental_customers import services


@admin.register(RegisteredRentalCustomer)
class RegisteredRentalCustomerAdmin(ObjectActionsMixin, admin.ModelAdmin):
    list_display = [
        "contact",
        "notes",
        "wants_sepa_mandate",
        "created_at",
        "processed",
    ]

    list_filter = [
        "processed",
    ]

    readonly_fields = [
        "created_at",
        "processed_at",
        "sepa_mandate_sent",
        "processed",
    ]

    search_fields = [
        "contact__first_name",
        "contact__last_name",
        "contact__company_name",
        "notes",
    ]

    date_hierarchy = "created_at"

    autocomplete_fields = [
        "contact",
        "assets",
        "agreement",
    ]

    object_actions_after_related_objects = [
        "send_sepa_mandate_request",
        "view_contact_on_moneybird",
        "process",
        "draft_agreement",
    ]

    @object_action(
        label=_("(Re)send SEPA mandate request"),
        confirmation=_(
            "Are you sure you want to send the customer a new SEPA mandate request?"
        ),
        log_message="(Re)sent SEPA mandate request",
    )
    def send_sepa_mandate_request(self, request, obj):
        services.send_sepa_mandate_request(obj)
        return True

    @object_action(
        label=_("View contact on Moneybird"),
    )
    def view_contact_on_moneybird(self, request, obj):
        return redirect(obj.contact.moneybird_url)

    @object_action(
        label=_("Mark processed"),
        extra_classes="default",
        log_message="Marked processed",
        perform_after_saving=True,
        condition=lambda request, obj: not obj.processed and obj.agreement,
        display_as_disabled_if_condition_not_met=True,
    )
    def process(self, request, obj):
        services.process(obj)
        return True

    @object_action(
        label=_("Create draft agreement"),
        extra_classes="default",
        log_message="Draft agreement created",
        perform_after_saving=True,
        condition=lambda request, obj: not obj.agreement,
    )
    def draft_agreement(self, request, obj):
        services.create_draft_agreement(obj)
        return True
