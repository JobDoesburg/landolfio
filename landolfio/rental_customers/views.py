import logging

from django.contrib import messages
from django.shortcuts import render
from django.views.generic import CreateView
from django.utils.translation import gettext_lazy as _

from rental_customers.forms import RentalCustomerRegistrationForm, ContactForm
from rental_customers.models import RegisteredRentalCustomer
from rental_customers.services import send_new_customer_notification


class NewCustomerRegistrationView(CreateView):
    model = RegisteredRentalCustomer
    form_class = RentalCustomerRegistrationForm
    template_name = "register-customer.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["contact"] = ContactForm(self.request.POST)
        else:
            data["contact"] = ContactForm()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        contact = context["contact"]
        if contact.is_valid():
            contact.save()
            obj = form.save()
            obj.contact = contact.instance
            try:
                obj.save()
                send_new_customer_notification(obj)
            except Exception as e:
                logging.error(e)
                messages.error(
                    self.request, _("Something went wrong. Please contact us.")
                )
                return self.form_invalid(form)
            return render(self.request, "register-customer-success.html")
        else:
            return self.form_invalid(form)
