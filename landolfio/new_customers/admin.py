from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django_easy_admin_object_actions.decorators import object_action

from new_customers.models import NEW_CUSTOMER_TICKET_TYPE
from new_rental_customers.models import NewCustomer
from new_rental_customers import services
from tickets.admin import TicketAdmin


@admin.register(NewCustomer)
class NewCustomerAdmin(TicketAdmin):
    ticket_type_id = NEW_CUSTOMER_TICKET_TYPE.id

    readonly_fields = TicketAdmin.readonly_fields + [
        "ticket_type",
        "sepa_mandate_sent",
        "title",
    ]

    fields = TicketAdmin.fields + [
        "wants_sepa_mandate",
        "sepa_mandate_sent",
    ]

    object_actions_after_fieldsets = [
        "send_sepa_mandate_request",
        "view_contact_on_moneybird",
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
