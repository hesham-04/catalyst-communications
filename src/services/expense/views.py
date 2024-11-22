from datetime import date

from django.core.checks import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from src.services.project.models import Project
from .forms import ExpenseForm, ExpenseFormCreate, VendorForm, ExpenseCategoryForm
from .models import Expense, Vendor, ExpenseCategory
from ..project.bll import create_expense_calculations


# List All Expense
class ExpenseIndexView(TemplateView):
    template_name = 'expense/expense_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expenses'] = Expense.objects.all().order_by('-created_at')
        return context

# Project Detail
class CreateExpenseView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense/expense_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.project = project # Associate the project with the expense.
        amount = form.cleaned_data['amount']
        budget_source = form.cleaned_data['budget_source']
        description = form.cleaned_data['description']
        vendor = form.cleaned_data['vendor']

        # Validate the amounts
        # Check for the source and deduct from project source.
        # Log this in the Ledger

        # Doing the Validation checks here, can not pass the form instance to the BLL.
        if amount <= 0:
            form.add_error('amount', 'Amount must be greater than zero.')
            return self.form_invalid(form)

        if budget_source == 'CASH':
            if amount > project.project_cash:
                form.add_error('amount', 'Amount exceeds project cash budget.')
                return self.form_invalid(form)

        if budget_source == 'ACC':
            if amount > project.project_account_balance:
                form.add_error('amount', 'Amount exceeds project account balance.')
                return self.form_invalid(form)


        create_expense_calculations(project_id=project.pk, amount=amount, budget_source=budget_source, reason=description)
        expense = form.save()
        return redirect(reverse('project:detail', kwargs={'pk': project.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        context['expenses'] = Expense.objects.filter(project=self.kwargs['pk'])
        context['total_expenses'] = self.get_total_expenses()
        context['expenses_today'] = self.get_expenses_today()
        return context

    def get_total_expenses(self):
        expenses = Expense.objects.filter(project=self.kwargs['pk'])
        total = sum(expense.amount for expense in expenses)
        return total

    def get_expenses_today(self):
        expenses = Expense.objects.filter(project=self.kwargs['pk'])
        today = date.today()
        expenses_today = expenses.filter(created_at__year=today.year, created_at__month=today.month,
                                         created_at__day=today.day)
        total = sum(expense.amount for expense in expenses_today)
        return total

# Independent Expense Creation
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseFormCreate
    template_name = 'expense/form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        project = self.object.project
        if self.object.budget_source == Expense.BudgetSource.CASH:
            project.cash_in_hand -= self.object.amount
        elif self.object.budget_source == Expense.BudgetSource.ACCOUNT:
            project.account -= self.object.amount
        elif self.object.budget_source == Expense.BudgetSource.CLIENT_FUNDS:
            project.client_funds -= self.object.amount
        elif self.object.budget_source == Expense.BudgetSource.LOAN:
            project.loan -= self.object.amount

        project.save()
        self.object.save()

        messages.success(self.request, "Expense created and project budget updated successfully.")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('expense:index', kwargs={'pk': self.object.project.pk})



class VendorCreateView(CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'expense/vendor_form.html'  # Define your HTML template
    success_url = reverse_lazy('expense:index')  # Redirect after creation

class ExpenseCategoryCreateView(CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expense/category_form.html'  # Define your HTML template
    success_url = reverse_lazy('expense:index')  # Redirect after creation