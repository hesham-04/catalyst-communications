from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, FormView, DeleteView

from src.services.project.bll import (
    add_loan_to_project,
    create_misc_loan,
    return_misc_loan,
)
from src.services.project.bll import return_loan_to_lender
from src.services.project.models import Project
from .forms import LoanForm, MiscLoanForm, MiscLoanReturnForm
from .forms import LoanReturnForm
from .models import Loan, LoanReturn, Lender, MiscLoan
from ..transaction.models import Ledger
from ...web.dashboard.utils import ledger_filter


# VALIDATION ✔
class LendLoanView(LoginRequiredMixin, CreateView):
    """
    Create a loan for a project [( PROJECT LOAN )]
    """

    form_class = LoanForm
    template_name = "loan/lend_loan.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Project, id=self.kwargs["pk"])

    def form_valid(self, form):
        loan = form.save(commit=False)
        lender = form.cleaned_data["lender"]
        amount = form.cleaned_data["loan_amount"]
        reason = form.cleaned_data["reason"]

        # No amount or balance checks needed because a loan is being created.
        if amount <= 0:
            form.add_error("loan_amount", "Amount must be greater than zero.")
            return self.form_invalid(form)
        loan.project = self.get_object()
        loan.save()

        # Make changes to the Project & Ledger before creating the loan Object
        add_loan_to_project(
            project_id=self.kwargs["pk"], amount=amount, source=loan, reason=reason
        )

        # Link the project to loan object

        messages.success(
            self.request,
            f"Loan of {amount} successfully created for project {self.get_object().project_name}.",
        )
        return redirect("project:detail", pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.get_object()  # For The GoBack Button (PK)
        return context


class LoanListView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = "loan/loan_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, id=self.kwargs["pk"])
        return context

    def get_queryset(self):
        return Loan.objects.filter(project=self.kwargs["pk"]).order_by("-due_date")


# VALIDATION ✔
class ReturnLoanView(LoginRequiredMixin, CreateView):
    form_class = LoanReturnForm
    template_name = "loan/return_loan.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Loan, id=self.kwargs["pk"])

    def form_valid(self, form):
        return_amount = form.cleaned_data["return_amount"]
        remarks = form.cleaned_data["remarks"]
        loan = self.get_object()

        loan_return = form.save(commit=False)

        # Validate the Form:

        if return_amount <= 0:
            form.add_error("return_amount", "Amount must be greater than zero.")
            return self.form_invalid(form)

        if return_amount > loan.remaining_amount:
            form.add_error(
                "return_amount", "The amount is more than the project loan amount."
            )
            return self.form_invalid(form)

        if return_amount > loan.project.project_account_balance:
            form.add_error(
                "return_amount", "The amount is more than Project account balance."
            )
            return self.form_invalid(form)

        # Create an expense Object for this project & Perform the return.
        return_loan_to_lender(
            project_id=loan.project.id,
            loan_id=loan.pk,
            amount=return_amount,
            reason=remarks,
        )

        loan_return.loan = loan
        loan_return.save()
        messages.success(
            self.request,
            f"Successfully recorded loan return of {return_amount} for "
            f"project {loan.project.project_name}.",
        )
        return redirect("project:detail", pk=loan.project.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        logs = Ledger.objects.filter(
            project=loan.project, transaction_type="RETURN_LOAN"
        )
        context["loan"] = loan
        context["project"] = loan.project
        context["return_logs"] = logs
        return context


class LenderListView(LoginRequiredMixin, ListView):
    model = Lender
    paginate_by = 25


class LenderDetailView(LoginRequiredMixin, DetailView):
    model = Lender

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        loans = self.object.loans.all()
        misc_loans = self.object.misc_loans.all()

        combined_loans = list(loans) + list(misc_loans)

        context["loans"] = combined_loans
        return context


class LenderCreateView(LoginRequiredMixin, CreateView):
    model = Lender
    fields = "__all__"
    success_url = reverse_lazy("loan:lenders")


# VALIDATION ✔
class MiscLoanCreateView(LoginRequiredMixin, CreateView):
    model = MiscLoan
    form_class = MiscLoanForm
    success_url = reverse_lazy("loan:lenders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lender"] = get_object_or_404(Lender, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):

        with transaction.atomic():
            misc_loan = form.save(commit=False)
            destination_account = form.cleaned_data["destination"]
            reason = form.cleaned_data["reason"]
            amount = form.cleaned_data["loan_amount"]

            if amount <= 0:
                form.add_error("loan_amount", "Amount must be greater than zero.")
                return self.form_invalid(form)
            misc_loan.save()

            success, message = create_misc_loan(
                destination_account=destination_account,
                misc_loan_pk=misc_loan.pk,
                reason=reason,
                amount=amount,
            )

        messages.success(self.request, f"Loan of amount {amount} created successfully")
        return super().form_valid(form)


class MiscLoanReturnView(LoginRequiredMixin, FormView):
    form_class = MiscLoanReturnForm
    template_name = "loan/misc_loan_return.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(MiscLoan, id=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return_amount = form.cleaned_data["return_amount"]
        account = form.cleaned_data["source"]
        remarks = form.cleaned_data["remarks"]
        loan = self.object

        if return_amount <= 0:
            form.add_error("return_amount", "Amount must be greater than zero.")
            return self.form_invalid(form)

        if return_amount > loan.remaining_amount:
            form.add_error(
                "return_amount", "The amount is more than the project loan amount."
            )
            return self.form_invalid(form)

        if return_amount > account.balance:
            form.add_error(
                "return_amount", "The amount is more than Project account balance."
            )
            return self.form_invalid(form)

        success, message = return_misc_loan(
            destination_account=self.object,
            source=account,
            reason=remarks,
            amount=return_amount,
        )

        messages.success(self.request, message)
        return redirect("loan:lender-detail", pk=loan.lender.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.object
        context["loan"] = loan
        context["return_logs"] = ledger_filter(
            destination=loan, transaction_type="MISC_LOAN_RETURN"
        )
        return context


class LenderDeleteView(LoginRequiredMixin, DeleteView):
    model = Lender
    success_url = reverse_lazy("loan:lenders")
    template_name = 'loan/lender_confirm_delete.html'
