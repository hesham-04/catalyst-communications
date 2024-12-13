from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView
from django.views.generic import TemplateView

from .forms import QuotationForm, QuotationItemForm
from .models import Quotation, QuotationItem
from ..project.models import Project


class CreateQuotationView(LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotation/quotation_form.html"  # Update to the correct template

    def get_initial(self):
        initial = super().get_initial()
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        initial["project"] = project
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = Project.objects.get(pk=self.kwargs["pk"])
        QuotationItemFormSet = modelformset_factory(
            QuotationItem, form=QuotationItemForm, extra=1
        )
        context["formset"] = QuotationItemFormSet(queryset=QuotationItem.objects.none())
        return context

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        form.instance.project = project
        quotation = form.save()

        project.project_status = Project.ProjectStatus.AWAITING
        project.save()

        QuotationItemFormSet = modelformset_factory(
            QuotationItem, form=QuotationItemForm
        )
        formset = QuotationItemFormSet(self.request.POST)

        if formset.is_valid():
            for item_form in formset:
                item_form.instance.quotation = quotation
                item_form.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("quotation:detail", kwargs={"pk": self.object.pk})


class PrintQuotationView(LoginRequiredMixin, TemplateView):
    template_name = "quotation/quotation_print.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotation"] = get_object_or_404(Quotation, pk=self.kwargs["pk"])
        return context


class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = "quotation/quotation_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotation"] = get_object_or_404(Quotation, pk=self.kwargs["pk"])
        return context
