import logging

from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from new_customers.forms import NewContactForm, NewCustomerForm
from new_customers.models import NewCustomer
from new_customers.services import send_new_customer_notification


class NewCustomerRegistrationView(CreateView):
    model = NewCustomer
    form_class = NewCustomerForm
    template_name = "register-customer.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # Add the contact form to the context in addition to the customer form
        if self.request.POST:
            # If the form is submitted, use the submitted data
            data["contact"] = NewContactForm(self.request.POST)
        else:
            # If the form is not submitted, use an empty form
            data["contact"] = NewContactForm()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        contact_form = context["contact"]

        # First, try to save the contact form
        if not contact_form.is_valid():
            # If the contact form is not valid, return the form with errors
            return self.form_invalid(form)

        contact = contact_form.save()

        # After saving the contact, save the new customer ticket with the newly created contact
        obj = form.save()
        obj.contact = contact

        try:
            obj.save()
        except Exception as e:
            # If something went wrong during saving, return the form with errors
            logging.error(e)
            messages.error(self.request, _("Something went wrong. Please contact us."))
            return self.form_invalid(form)

        try:
            # Notify the admin about the new customer
            send_new_customer_notification(obj)
        except Exception as e:
            # If something went wrong during sending the email, log the error, but don't let the user know
            logging.error(e)

        if obj.wants_sepa_mandate:
            # If the customer requested a SEPA mandate, show them a different success page
            mandate_url = None
            try:
                mandate_url = obj.contact.get_payments_mandate_url()
            except Exception as e:
                logging.warning(
                    f"Could not get SEPA mandate URL (possibly demo administration): {e}"
                )

            return render(
                self.request,
                "register-customer-success-sepa.html",
                {"mandate_url": mandate_url},
            )

        return render(self.request, "register-customer-success.html")
