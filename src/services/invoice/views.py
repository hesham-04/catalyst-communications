from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
from .models import Invoice, InvoiceItem
from ..project.bll import process_invoice_payment
from ..project.models import Project


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

    # noinspection PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=kwargs["pk"])
        form = TransferFundsForm()
        return render(
            request, "invoice/invoice_paid.html", {"form": form, "invoice": invoice}
        )

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=kwargs["pk"])
        form = TransferFundsForm(request.POST)

        if form.is_valid():
            account = form.cleaned_data[
                "account"
            ]  # This is a model instance of The AccountBalance Model
            amount = invoice.total_amount

            # Processing the invoice payment
            success, message = process_invoice_payment(
                invoice_id=invoice.pk,
                account_id=account.pk,
                amount=amount,
            )

            if success:
                messages.success(
                    request,
                    f"{amount} Funds Successfully Transferred to {account.account_name}.",
                )
                return redirect(reverse("project:detail", args=[invoice.project.pk]))
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
