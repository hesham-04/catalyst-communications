from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from .forms import InvoiceForm, InvoiceItemForm
from .models import Invoice, InvoiceItem
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

        if formset.is_valid():
            for item_form in formset:
                item_form.instance.invoice = invoice
                item_form.save()

        # Recalculate the total amount after items are added
        invoice.calculate_total_amount()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('invoice:print', kwargs={'pk': self.object.pk})


class PrintInvoiceView(TemplateView):
    template_name = 'invoice/invoice_print.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = get_object_or_404(Invoice, pk=self.kwargs['pk'])
        return context
