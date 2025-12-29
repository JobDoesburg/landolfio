from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django_easy_admin_object_actions.decorators import object_action

from new_customers.admin import NewCustomerAdmin
from new_rental_customers import services
from new_rental_customers.models import (
    NewRentalCustomer,
    get_rental_customer_ticket_type,
)


@admin.register(NewRentalCustomer)
class NewRentalCustomerAdmin(NewCustomerAdmin):
    readonly_fields = NewCustomerAdmin.readonly_fields

    def _get_ticket_type_id(self):
        return get_rental_customer_ticket_type().id

    fieldsets = (
        NewCustomerAdmin.fieldsets[:1]
        + [
            (
                _("New rental customer"),
                {
                    "fields": (
                        (
                            "wants_reduced_liability",
                            "rental_price",
                            "date_received",
                            "affiliate_name",
                            "instrument_numbers",
                        )
                    )
                },
            ),
        ]
        + NewCustomerAdmin.fieldsets[1:]
    )

    object_actions_after_fieldsets = NewCustomerAdmin.object_actions_after_fieldsets + [
        "draft_agreement",
    ]

    @object_action(
        label=_("Create draft agreement"),
        extra_classes="default",
        log_message="Draft agreement created",
        perform_after_saving=True,
    )
    def draft_agreement(self, request, obj):
        services.create_draft_agreement(obj)
        return True
