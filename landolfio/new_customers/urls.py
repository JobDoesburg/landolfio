from django.urls import path

from .views import *

app_name = "new_customers"

urlpatterns = [
    path(
        "new/",
        NewCustomerRegistrationView.as_view(),
        name="new-customer",
    ),
]
