from new_customers.views import NewCustomerRegistrationView
from new_rental_customers.forms import NewRentalCustomerForm
from new_rental_customers.models import NewRentalCustomer


class NewRentalCustomerRegistrationView(NewCustomerRegistrationView):
    model = NewRentalCustomer
    form_class = NewRentalCustomerForm
    template_name = "register-rental-customer.html"
