from django.contrib import admin
from django.shortcuts import redirect
from django.template import loader
from django_easy_admin_object_actions.admin import ObjectActionsMixin
from django.utils.translation import gettext_lazy as _
from django_easy_admin_object_actions.decorators import object_action

from rental_customers.models import RegisteredRentalCustomer


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
    ]

    object_actions_after_related_objects = [
        "send_sepa_mandate_request",
        "view_contact_on_moneybird",
        "process",
    ]

    @object_action(
        label=_("(Re)send SEPA mandate request"),
        parameter_name="_sendsepamandaterequest",
        confirmation=_(
            "Are you sure you want to send the customer a new SEPA mandate request?"
        ),
        log_message="(Re)sent SEPA mandate request",
    )
    def send_sepa_mandate_request(self, request, obj):
        if obj:
            obj.contact.request_payments_mandate(
                message=loader.render_to_string(
                    "email/mandate_request_message.txt", {"customer": obj.contact}
                )
            )

    @object_action(
        label=_("View contact on Moneybird"),
        parameter_name="_viewcontactmoneybird",
    )
    def view_contact_on_moneybird(self, request, obj):
        if obj:
            return redirect(obj.contact.moneybird_url)

    @object_action(
        label=_("Mark processed"),
        parameter_name="_process",
        extra_classes="default",
        log_message="Marked processed",
        perform_after_saving=True,
        condition=lambda request, obj: not obj.processed,
    )
    def process(self, request, obj):
        if obj:
            obj.processed = True
            obj.save()
