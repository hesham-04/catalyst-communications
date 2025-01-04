from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, FormView, DeleteView

from src.services.project.models import Project
from .forms import (
    ExpenseForm,
    ExpenseCategoryForm,
    ExpensePaymentForm,
    JournalExpenseForm,
    DateRangeForm,
)
from .models import Expense, ExpenseCategory, JournalExpense
from ..assets.models import CashInHand, AccountBalance
from ..charts.views import generate_expense_report
from ..project.bll import (
    create_expense_calculations,
    pay_expense,
    create_journal_expense_calculations,
)
from ..transaction.models import Ledger


class ExpenseIndexView(LoginRequiredMixin, TemplateView):
    template_name = "expense/expense_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        expenses_list = Ledger.objects.filter(transaction_type="MISC_EXPENSE").order_by(
            "-created_at"
        )

        paginator = Paginator(expenses_list, 20)
        page_number = self.request.GET.get("page", 1)
        try:
            expenses_page = paginator.page(page_number)
        except Exception as e:
            raise Http404("Invalid page number.")
        form = DateRangeForm()

        context["entries"] = expenses_page
        context["form"] = form

        return context

    def post(self, request, *args, **kwargs):
        form = DateRangeForm(request.POST)

        if form.is_valid():
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")

            if start_date and end_date:
                return generate_expense_report(request, start_date, end_date)
            else:
                print("Form is not valid")
            return self.get(request, *args, **kwargs)


# VALIDATION ✔
class CreateExpenseView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expense/expense_form.html"

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        form.instance.project = project  # Associate the project with the expense.

        amount = form.cleaned_data["amount"]
        budget_source = form.cleaned_data["budget_source"]
        description = form.cleaned_data["description"]
        vendor = form.cleaned_data["vendor"]
        category = form.cleaned_data["category"]

        # Validate the amounts
        # Check for the source and deduct from project source.
        # Log this in the Ledger

        # Doing the Validation checks here, can not pass the form instance to the BLL.
        if amount <= 0:
            form.add_error("amount", "Amount must be greater than zero.")
            return self.form_invalid(form)

        if budget_source == "CASH":
            if amount > project.project_cash:
                form.add_error("amount", "Amount exceeds project cash budget.")
                return self.form_invalid(form)

        if budget_source == "ACC":
            if amount > project.project_account_balance:
                form.add_error("amount", "Amount exceeds project account balance.")
                return self.form_invalid(form)
        expense = form.save()

        create_expense_calculations(
            project_id=project.pk,
            amount=amount,
            budget_source=budget_source,
            vendor_pk=vendor.pk,
            reason=description,
            category=category,
            expense=expense,
        )

        return redirect(reverse("project:detail", kwargs={"pk": project.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["pk"])
        context["expenses"] = Expense.objects.filter(project=self.kwargs["pk"])
        context["total_expenses"] = Expense.calculate_total_expenses(
            project_id=self.kwargs["pk"]
        )
        context["expenses_today"] = Expense.calculate_total_expenses(
            project_id=self.kwargs["pk"], start_date=date.today()
        )
        return context


# DEPRECATED †
class ExpensePaymentView(LoginRequiredMixin, FormView):
    template_name = "expense/expense_payment.html"
    form_class = ExpensePaymentForm
    success_url = reverse_lazy("expense:index")

    def form_valid(self, form):
        expense = get_object_or_404(Expense, pk=self.kwargs["pk"])
        project = expense.project
        source = form.cleaned_data["source"]
        remarks = form.cleaned_data["remarks"]

        # Validate the data
        if source == "CASH":
            if expense.amount > expense.project.project_cash:
                form.add_error("amount", "Amount exceeds project cash budget.")
                return self.form_invalid(form)
        elif source == "ACC":
            if expense.amount > expense.project.project_account_balance:
                form.add_error("amount", "Amount exceeds project account balance.")
                return self.form_invalid(form)

        # Deduct the amount from the source
        pay_expense(
            project_id=project.pk,
            expense_id=expense.pk,
            budget_source=source,
            destination=expense.vendor,
            amount=expense.amount,
            reason=remarks,
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["expense"] = get_object_or_404(Expense, pk=self.kwargs["pk"])
        context["project"] = context["expense"].project
        return context


class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = "expense/category_form.html"  # Define your HTML template
    success_url = reverse_lazy("expense:expense-category-list")  # Redirect after creation


class ExpenseCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenseCategory
    success_url = reverse_lazy("expense:expense-category-list")


class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenseCategory
    paginate_by = 20


# VALIDATION ✔
class JournalExpenseCreateView(LoginRequiredMixin, CreateView):
    model = JournalExpense
    form_class = JournalExpenseForm
    success_url = reverse_lazy("expense:index")
    template_name = "expense/journal_expense_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cash_in_hand"] = (
            CashInHand.objects.first().balance if CashInHand.objects.exists() else 0
        )
        context["account_balance"] = AccountBalance.get_total_balance()
        context["expenses_today"] = JournalExpense.calculate_total_expenses(
            start_date=date.today()
        )
        return context

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        source = form.cleaned_data["budget_source"]
        destination = form.cleaned_data["vendor"]
        description = form.cleaned_data["description"]
        category = form.cleaned_data["category"]

        # If source is ACC then we need an instance, else we have only one CIH instance
        if source == "ACC":
            account = form.cleaned_data[
                "account"
            ]  # If ACC an Account Object Instance is provided by the form
            if account.balance < amount:
                form.add_error(
                    "amount", "The selected account does not have enough funds."
                )
                return self.form_invalid(form)

        else:
            cash = CashInHand.objects.first()
            if not cash:
                form.add_error("budget_source", "Cash in hand record not found.")
                return self.form_invalid(form)
            if cash.balance < amount:
                form.add_error("amount", "Not enough cash in hand.")
                return self.form_invalid(form)

        if amount <= 0:
            form.add_error("amount", "Amount must be greater than zero.")
            return self.form_invalid(form)

        misc_expense = form.save(commit=False)
        misc_expense.save()

        success, message = create_journal_expense_calculations(
            category=category,
            reason=description,
            vendor=destination,
            amount=amount,
            source=source,
            misc_expense=misc_expense,
            account_pk=account.pk if source == "ACC" and account else None,
        )
        if not success:
            form.add_error("budget_source", message)
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"General expense {form.cleaned_data['description']} "
            f"of {form.cleaned_data['amount']} has been successfully created!",
        )
        return super().form_valid(form)
