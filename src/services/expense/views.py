from datetime import date
from django.core.checks import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, FormView
from src.services.project.models import Project
from .forms import ExpenseForm, ExpenseFormCreate, ExpenseCategoryForm, ExpensePaymentForm
from .models import Expense, ExpenseCategory
from ..project.bll import create_expense_calculations, pay_expense


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

class ExpensePaymentView(FormView):
    template_name = 'expense/expense_payment.html'
    form_class = ExpensePaymentForm
    success_url = reverse_lazy('expense:index')


    def form_valid(self, form):
        expense = get_object_or_404(Expense, pk=self.kwargs['pk'])
        project = expense.project
        source = form.cleaned_data['source']
        remarks = form.cleaned_data['remarks']

        # Validate the data
        if source == 'CASH':
            if expense.amount > expense.project.project_cash:
                form.add_error('amount', 'Amount exceeds project cash budget.')
                return self.form_invalid(form)
        elif source == 'ACC':
            if expense.amount > expense.project.project_account_balance:
                form.add_error('amount', 'Amount exceeds project account balance.')
                return self.form_invalid(form)

        # Deduct the amount from the source
        pay_expense(project_id=project.pk, expense_id=expense.pk, budget_source=source, destination=expense.vendor, amount=expense.amount, reason=remarks)
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense'] = get_object_or_404(Expense, pk=self.kwargs['pk'])
        context['project'] = context['expense'].project
        return context


class ExpenseCategoryCreateView(CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expense/category_form.html'  # Define your HTML template
    success_url = reverse_lazy('expense:index')  # Redirect after creation