from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.views.generic import TemplateView

from .forms import (
    QuotationForm,
    QuotationItemForm,
    QuotationUpdateForm,
    ItemGeneralForm,
    QuotationGeneralForm,
)
from .models import Quotation, QuotationItem, ItemGeneral, QuotationGeneral
from ..project.models import Project


class CreateQuotationView(LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotation/quotation_form.html"

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

    @transaction.atomic
    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        form.instance.project = project
        project.project_status = Project.ProjectStatus.AWAITING

        # Creating formset for QuotationItem
        quotation_item_form_set = modelformset_factory(
            QuotationItem, form=QuotationItemForm
        )
        formset = quotation_item_form_set(self.request.POST)

        if formset.is_valid():
            # Only Save if the form and formset are valid
            quotation = form.save()
            project.save()

            for item_form in formset:
                item_form.instance.quotation = quotation
                quotation.calculate_total_amount()
                item_form.save()

            # SET TAX TO FALSE IF TAX ON ALL ITEMS IS 0.0
            for item in quotation.items.all():
                if item.tax == 0.0:
                    quotation.tax = False

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
        return reverse("quotation:detail", kwargs={"pk": self.object.pk})


class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = "quotation/quotation_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotation"] = get_object_or_404(Quotation, pk=self.kwargs["pk"])
        return context


class QuotationUpdateView(LoginRequiredMixin, UpdateView):
    model = Quotation
    form_class = QuotationUpdateForm
    template_name = "quotation/quotation_edit.html"

    def get_success_url(self):
        return reverse("quotation:detail", kwargs={"pk": self.object.pk})


class GeneralView(ListView, LoginRequiredMixin):
    template_name = "quotation/general.html"
    model = QuotationGeneral


class CreateGeneralQuotationView(LoginRequiredMixin, CreateView):
    model = QuotationGeneral
    form_class = QuotationGeneralForm
    template_name = "quotation/quotation_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        QuotationItemFormSet = modelformset_factory(
            ItemGeneral, form=QuotationItemForm, extra=1
        )
        context["formset"] = QuotationItemFormSet(queryset=ItemGeneral.objects.none())
        return context

    @transaction.atomic
    def form_valid(self, form):

        # Creating formset for QuotationItem
        quotation_item_form_set = modelformset_factory(
            ItemGeneral, form=ItemGeneralForm, extra=1
        )
        formset = quotation_item_form_set(self.request.POST)

        if formset.is_valid():
            # Only Save if the form and formset are valid
            quotation = form.save()

            for item_form in formset:
                item_form.instance.quotation = quotation
                quotation.calculate_total_amount()
                item_form.save()

            # SET TAX TO FALSE IF TAX ON ALL ITEMS IS 0.0
            for item in quotation.items.all():
                if item.tax == 0.0:
                    quotation.tax = False

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
            return redirect("quotation:open-market")

    def get_success_url(self):
        return reverse("quotation:open-market")


class GeneralQuotationDetailView(LoginRequiredMixin, DetailView):
    model = QuotationGeneral
    template_name = "quotation/quotation_general_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotation"] = get_object_or_404(QuotationGeneral, pk=self.kwargs["pk"])
        return context


def invoice_gen_quote(request, pk):
    quotation = get_object_or_404(QuotationGeneral, pk=pk)
    quotation.status = "INVOICED"
    quotation.save()
    return redirect("quotation:general_detail", pk=quotation.pk)
