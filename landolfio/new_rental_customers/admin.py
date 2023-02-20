from django.contrib import admin
from django_easy_admin_object_actions.decorators import object_action
from django.utils.translation import gettext_lazy as _

from new_customers.admin import NewCustomerAdmin
from new_rental_customers import services
from new_rental_customers.models import (
    NewRentalCustomer,
    NEW_RENTAL_CUSTOMER_TICKET_TYPE,
)


@admin.register(NewRentalCustomer)
class NewRentalCustomerAdmin(NewCustomerAdmin):
    readonly_fields = NewCustomerAdmin.readonly_fields
    ticket_type_id = NEW_RENTAL_CUSTOMER_TICKET_TYPE.id

    fields = NewCustomerAdmin.fields + [
        "wants_reduced_liability",
        "affiliate_name",
        "instrument_numbers",
        "rental_price",
    ]

    object_actions_after_fieldsets = NewCustomerAdmin.object_actions_after_fieldsets + [
        "draft_agreement",
    ]

    @object_action(
        label=_("Create draft agreement"),
        extra_classes="default",
        log_message="Draft agreement created",
        perform_after_saving=True,
        condition=lambda request, obj: not obj.estimates,
    )
    def draft_agreement(self, request, obj):
        services.create_draft_agreement(obj)
        return True
