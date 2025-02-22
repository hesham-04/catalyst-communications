from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    TemplateView,
    DetailView,
    DeleteView,
    UpdateView,
)

from .forms import InvoiceForm, InvoiceItemForm, TransferFundsForm, InvoiceUpdateForm
from .models import Invoice, InvoiceItem, DeliveryChallan, DeliveryChallanItem
from ..project.bll import process_invoice_payment
from ..project.models import Project
from ..quotation.models import QuotationGeneral


class CreateInvoiceView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "invoice/invoice_form.html"

    def get_initial(self):
        initial = super().get_initial()
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        initial["project"] = project
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = Project.objects.get(pk=self.kwargs["pk"])
        invoice_item_form_set = modelformset_factory(
            InvoiceItem, form=InvoiceItemForm, extra=1
        )
        context["formset"] = invoice_item_form_set(queryset=InvoiceItem.objects.none())
        return context

    @transaction.atomic
    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        form.instance.project = project
        invoice = form.save()

        invoice_item_formset = modelformset_factory(InvoiceItem, form=InvoiceItemForm)
        formset = invoice_item_formset(self.request.POST)

        if formset.is_valid():
            for item_form in formset:
                item_form.instance.invoice = invoice
                item_form.save()

            # SET TAX TO FALSE IF TAX ON ALL ITEMS IS 0.0
            for item in invoice.items.all():
                if item.tax == 0.0:
                    invoice.tax = False

            return super().form_valid(form)
        else:
            # Collect errors and display them as messages
            error_list = []
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        error_list.append(f"{field}: {error}")

            # Add the errors to the messages framework
            for error in error_list:
                messages.error(self.request, error)

            # Redirect to the project detail page
            project_id = self.get_initial()["project"].pk
            return redirect("project:detail", pk=project_id)

    def get_success_url(self):
        return reverse("invoice:detail", kwargs={"pk": self.object.pk})


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "invoice/invoice_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoice"] = get_object_or_404(Invoice, pk=self.kwargs["pk"])
        return context


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice

    def get_success_url(self):
        invoice = get_object_or_404(Invoice, pk=self.kwargs["pk"])
        return reverse_lazy("project:detail", kwargs={"pk": invoice.project.pk})


# VALIDATION ✔
class InvoicePaidView(LoginRequiredMixin, View):

    def get(self, request, q=False, *args, **kwargs):
        if q == True:
            request.session["quote"] = True
            invoice = get_object_or_404(QuotationGeneral, pk=kwargs["pk"])
        else:
            request.session["quote"] = False
            invoice = get_object_or_404(Invoice, pk=kwargs["pk"])

        form = TransferFundsForm()
        return render(
            request, "invoice/invoice_paid.html", {"form": form, "invoice": invoice}
        )

    def post(self, request, *args, **kwargs):
        quote = request.session.get("quote", False)

        if quote:
            invoice = get_object_or_404(QuotationGeneral, pk=kwargs["pk"])
        else:
            invoice = get_object_or_404(Invoice, pk=kwargs["pk"])

        form = TransferFundsForm(request.POST)

        if form.is_valid():
            account = form.cleaned_data["account"]
            amount = invoice.total_amount

            success, message = process_invoice_payment(
                invoice_id=invoice.pk,
                account_id=account.pk,
                amount=amount,
                q=quote,
            )

            if success:
                messages.success(
                    request,
                    f"{amount} Funds Successfully Transferred to {account.account_name}.",
                )
                if quote:
                    return redirect(
                        reverse("quotation:general_detail", args=[invoice.pk])
                    )
                else:
                    return redirect(
                        reverse("project:detail", args=[invoice.project.pk])
                    )
            else:
                messages.error(request, message)
                return render(
                    request,
                    "invoice/invoice_paid.html",
                    {"form": form, "invoice": invoice},
                )

        return render(
            request, "invoice/invoice_paid.html", {"form": form, "invoice": invoice}
        )


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceUpdateForm
    template_name = "invoice/invoice_edit.html"

    def get_success_url(self):
        return reverse("invoice:detail", kwargs={"pk": self.object.pk})


class UpdateInvoiceView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "invoice/invoice_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()

        # Allow adding new items by setting extra > 0
        invoice_item_form_set = modelformset_factory(
            InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True
        )
        if self.request.POST:
            context["formset"] = invoice_item_form_set(
                self.request.POST, queryset=invoice.items.all()
            )
        else:
            context["formset"] = invoice_item_form_set(queryset=invoice.items.all())

        context["project"] = invoice.project  # Include project context if necessary
        return context

    @transaction.atomic
    def form_valid(self, form):
        invoice = form.save()

        # Process the formset for InvoiceItem objects
        invoice_item_form_set = modelformset_factory(
            InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True
        )
        formset = invoice_item_form_set(self.request.POST, queryset=invoice.items.all())

        if formset.is_valid():
            for item_form in formset:
                if item_form.cleaned_data.get("DELETE"):
                    # Handle deletion of items
                    item_form.instance.delete()
                elif item_form.cleaned_data:  # Save only non-empty forms
                    item_form.instance.invoice = invoice
                    item_form.save()

            # Adjust tax logic if necessary
            invoice.tax = any(item.tax != 0.0 for item in invoice.items.all())
            invoice.save()

            return super().form_valid(form)
        else:
            # Collect and display errors
            error_list = []
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        error_list.append(f"{field}: {error}")
            for error in error_list:
                messages.error(self.request, error)

            return redirect("invoice:detail", pk=invoice.pk)

    def get_success_url(self):
        return reverse("invoice:detail", kwargs={"pk": self.object.pk})


class DeliveryChallanView(LoginRequiredMixin, DetailView):
    model = DeliveryChallan
    template_name = "invoice/delivery_challan.html"
    context_object_name = "challan"

    def get_object(self):
        invoice_id = self.kwargs["invoice_id"]

        # Convert invoice_id safely
        try:
            invoice_id_int = int(invoice_id)
        except ValueError:
            raise ValueError("Invalid invoice ID format")  # Handle bad input

        # Try fetching the invoice from both models
        invoice = None
        content_type = None
        if Invoice.objects.filter(pk=invoice_id).exists():
            invoice = get_object_or_404(Invoice, pk=invoice_id)
            content_type = ContentType.objects.get_for_model(Invoice)
        elif QuotationGeneral.objects.filter(pk=invoice_id).exists():
            invoice = get_object_or_404(QuotationGeneral, pk=invoice_id)
            content_type = ContentType.objects.get_for_model(QuotationGeneral)
        else:
            raise ValueError("Invoice ID not found in either Invoice or QuotationGeneral models.")

        # Fetch or create the delivery challan with the same PK as the invoice
        challan, created = DeliveryChallan.objects.get_or_create(
            pk=invoice.pk,  # Set the PK of the challan to match the invoice's PK
            defaults={
                "content_type": content_type,
                "object_id": invoice.pk,
                "date": invoice.date,
                "client_name": invoice.client_name,
                "company_name": invoice.company_name,
                "phone": invoice.phone,
                "address": invoice.address,
                "email": invoice.email,
                "subject": invoice.subject,
                "notes": invoice.notes,
                "total_amount": invoice.total_amount,
                "total_in_words": invoice.total_in_words,
                "delivered_by": "Warehouse",  # Default value
                "received_by": "Client",  # Default value
            }
        )

        # If the challan was just created, populate its items
        if created:
            self.populate_challan_items(challan, invoice)

        return challan

    def populate_challan_items(self, challan, invoice):
        """
        Helper method to populate DeliveryChallanItem objects
        based on the associated InvoiceItem or ItemGeneral objects.
        """
        invoice_items = invoice.items.all()  # Fetch items once
        item_content_type = ContentType.objects.get_for_model(invoice_items.first())  # Detect item model
        DeliveryChallanItem.objects.bulk_create([
            DeliveryChallanItem(
                challan=challan,
                content_type=item_content_type,  # Store the correct item type
                object_id=item.id,  # Store the correct item ID
                item_name=item.item_name,
                description=item.description,
                quantity=item.quantity,
                rate=item.rate,
                amount=item.amount,
                tax=item.tax if item.tax else 0,
            )
            for item in invoice_items
        ])

class DeleteDeliveryChallanView(View):
    """
    Deletes a DeliveryChallan and redirects to a specified URL.
    """

    def post(self, request, challan_id):
        try:
            challan = get_object_or_404(DeliveryChallan, pk=challan_id)

            challan.delete()

            messages.success(request, "Delivery Challan regenerated successfully.")

        except Exception as e:
            messages.error(request, f"An error occurred while deleting the Delivery Challan: {str(e)}")

        return redirect(reverse("invoice:generate_challan", args=[challan_id]))  # ✅ Correct
