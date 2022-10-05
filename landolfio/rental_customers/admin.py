from django.contrib import admin

from rental_customers.models import RegisteredRentalCustomer


@admin.register(RegisteredRentalCustomer)
class RegisteredRentalCustomerAdmin(admin.ModelAdmin):
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
