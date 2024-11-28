from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView

from .forms import InvoiceForm, InvoiceItemForm, TransferFundsForm
from .models import Invoice, InvoiceItem
from ..project.bll import process_invoice_payment
from ..project.models import Project


class CreateInvoiceView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoice/invoice_form.html'

    def get_initial(self):
        initial = super().get_initial()
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        initial['project'] = project
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        InvoiceItemFormSet = modelformset_factory(InvoiceItem, form=InvoiceItemForm, extra=1)
        context['formset'] = InvoiceItemFormSet(queryset=InvoiceItem.objects.none())

        return context

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.project = project
        invoice = form.save()

        InvoiceItemFormSet = modelformset_factory(InvoiceItem, form=InvoiceItemForm)
        formset = InvoiceItemFormSet(self.request.POST)

        print(self.request.POST)

        if formset.is_valid():
            print("Formset is valid")
        else:
            print("Formset errors:", formset.errors)

        if formset.is_valid():
            for item_form in formset:
                item_form.instance.invoice = invoice
                item_form.save()

        # Recalculate the total amount after items are added
        invoice.calculate_total_amount()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('invoice:detail', kwargs={'pk': self.object.pk})


class PrintInvoiceView(TemplateView):
    template_name = 'invoice/invoice_print.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        return context


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoice/invoice_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        return context


class InvoicePaidView(View):
    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=kwargs['pk'])
        form = TransferFundsForm()
        return render(request, 'invoice/invoice_paid.html', {'form': form, 'invoice': invoice})

    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=kwargs['pk'])
        form = TransferFundsForm(request.POST)

        if form.is_valid():
            account = form.cleaned_data['account']
            amount = invoice.total_amount

            # Processing the invoice payment
            success, message = process_invoice_payment(
                invoice_id=invoice.pk,
                destination='account',
                account_id=account.pk,
                amount=amount
            )

            if success:
                messages.success(request, 'Funds Successfully Transferred')
                return redirect(reverse('project:detail', args=[invoice.project.pk]))
            else:
                messages.error(request, message)
                return render(request, 'invoice/invoice_paid.html', {'form': form, 'invoice': invoice})

        return render(request, 'invoice/invoice_paid.html', {'form': form, 'invoice': invoice})
