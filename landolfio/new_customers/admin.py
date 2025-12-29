from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django_easy_admin_object_actions.decorators import object_action

from new_customers.models import get_customer_ticket_type
from new_rental_customers import services
from new_rental_customers.models import NewCustomer
from tickets.admin import TicketAdmin


@admin.register(NewCustomer)
class NewCustomerAdmin(TicketAdmin):
    def _get_ticket_type_id(self):
        return get_customer_ticket_type().id

    readonly_fields = TicketAdmin.readonly_fields + [
        "ticket_type",
        "sepa_mandate_sent",
    ]

    fieldsets = (
        TicketAdmin.fieldsets[:1]
        + [
            (
                _("New customer"),
                {
                    "fields": (
                        (
                            "wants_sepa_mandate",
                            "sepa_mandate_sent",
                        )
                    )
                },
            ),
        ]
        + TicketAdmin.fieldsets[1:]
    )

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
