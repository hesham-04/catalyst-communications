from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, IntegrityError
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
            try:
                quotation = form.save()
            except IntegrityError  as e:
                print(e)
                messages.error(self.request, "Quotation already exists for this project")
                return redirect("project:detail", pk=project.pk)
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


class UpdateQuotationView(LoginRequiredMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = "quotation/quotation_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quotation = self.get_object()

        # Allow adding new items by setting extra > 0
        QuotationItemFormSet = modelformset_factory(
            QuotationItem, form=QuotationItemForm, extra=1, can_delete=True
        )
        if self.request.POST:
            context["formset"] = QuotationItemFormSet(
                self.request.POST, queryset=quotation.items.all()
            )
        else:
            context["formset"] = QuotationItemFormSet(queryset=quotation.items.all())

        context["project"] = quotation.project  # Include project context if needed
        return context

    @transaction.atomic
    def form_valid(self, form):
        quotation = form.save()

        # Process the formset for QuotationItem objects
        QuotationItemFormSet = modelformset_factory(
            QuotationItem, form=QuotationItemForm, extra=1, can_delete=True
        )
        formset = QuotationItemFormSet(
            self.request.POST, queryset=quotation.items.all()
        )

        if formset.is_valid():
            for item_form in formset:
                if item_form.cleaned_data.get("DELETE"):
                    # Handle deletion of items
                    item_form.instance.delete()
                elif item_form.cleaned_data:  # Save only non-empty forms
                    item_form.instance.quotation = quotation
                    item_form.save()

            # Recalculate total amount
            quotation.calculate_total_amount()

            # Adjust tax logic if necessary
            quotation.tax = any(item.tax != 0.0 for item in quotation.items.all())
            quotation.save()

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

            return redirect("quotation:detail", pk=quotation.pk)

    def get_success_url(self):
        return reverse("quotation:detail", kwargs={"pk": self.object.pk})


def invoice_gen_quote(request, pk):
    quotation = get_object_or_404(QuotationGeneral, pk=pk)
    quotation.status = "INVOICED"
    quotation.save()
    return redirect("quotation:general_detail", pk=quotation.pk)


class UpdateGeneralQuotationView(LoginRequiredMixin, UpdateView):
    model = QuotationGeneral
    form_class = QuotationGeneralForm
    template_name = "quotation/quotation_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quotation = self.get_object()

        # Create formset for ItemGeneral with existing items
        QuotationItemFormSet = modelformset_factory(
            ItemGeneral, form=ItemGeneralForm, extra=1, can_delete=True
        )
        if self.request.POST:
            context["formset"] = QuotationItemFormSet(
                self.request.POST, queryset=quotation.items.all()
            )
        else:
            context["formset"] = QuotationItemFormSet(queryset=quotation.items.all())

        return context

    @transaction.atomic
    def form_valid(self, form):
        quotation = form.save()

        # Handle formset for ItemGeneral objects
        QuotationItemFormSet = modelformset_factory(
            ItemGeneral, form=ItemGeneralForm, extra=1, can_delete=True
        )
        formset = QuotationItemFormSet(
            self.request.POST, queryset=quotation.items.all()
        )

        if formset.is_valid():
            for item_form in formset:
                if item_form.cleaned_data.get("DELETE"):
                    # Delete the item if marked for deletion
                    item_form.instance.delete()
                elif item_form.cleaned_data:  # Save valid forms
                    item_form.instance.quotation = quotation
                    item_form.save()

            # Recalculate total amount
            quotation.calculate_total_amount()

            # Set tax to False if no items have tax
            quotation.tax = any(item.tax != 0.0 for item in quotation.items.all())
            quotation.save()

            return super().form_valid(form)
        else:
            # Handle errors and display as messages
            error_list = []
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        error_list.append(f"{field}: {error}")

            for error in error_list:
                messages.error(self.request, error)

            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("quotation:general_detail", kwargs={"pk": self.object.pk})



class GeneralQuotationUpdateView(LoginRequiredMixin, UpdateView):
    model = QuotationGeneral
    form_class = QuotationGeneralForm
    template_name = "quotation/quotation_general_edit.html"

    def get_success_url(self):
        return reverse("quotation:general_detail", kwargs={"pk": self.object.pk})
