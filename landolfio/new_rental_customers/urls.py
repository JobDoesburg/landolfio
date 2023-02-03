from django.urls import path

from .views import *

app_name = "new_rental_customers"

urlpatterns = [
    path(
        "new/",
        NewRentalCustomerRegistrationView.as_view(),
        name="new-rental-customer",
    ),
]
