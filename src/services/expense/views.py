from datetime import date

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, FormView, DeleteView

from src.services.project.models import Project
from .forms import ExpenseForm, ExpenseCategoryForm, ExpensePaymentForm, JournalExpenseForm
from .models import Expense, ExpenseCategory, JournalExpense
from ..assets.models import CashInHand, AccountBalance
from ..project.bll import create_expense_calculations, pay_expense, create_journal_expense_calculations


class ExpenseIndexView(TemplateView):
    template_name = 'expense/expense_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        expenses_list = JournalExpense.objects.all().order_by('-created_at')

        paginator = Paginator(expenses_list, 10)  # 10 items per page
        page_number = self.request.GET.get('page', 1)
        try:
            expenses_page = paginator.page(page_number)
        except Exception as e:
            raise Http404("Invalid page number.")

        context['expenses'] = expenses_page
        return context


class CreateExpenseView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense/expense_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.project = project  # Associate the project with the expense.
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

        create_expense_calculations(project_id=project.pk, amount=amount, budget_source=budget_source,
                                    destination=vendor.pk, reason=description)
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
        pay_expense(project_id=project.pk, expense_id=expense.pk, budget_source=source, destination=expense.vendor,
                    amount=expense.amount, reason=remarks)
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

class ExpenseCategoryDeleteView(DeleteView):
    model = ExpenseCategory


class ExpenseCategoryListView(ListView):
    model = ExpenseCategory
    paginate_by = 20


class JournalExpenseCreateView(CreateView):
    model = JournalExpense
    form_class = JournalExpenseForm
    success_url = reverse_lazy('assets:index')
    template_name = 'expense/journalexpense_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cashinhand'] = CashInHand.objects.first().balance if CashInHand.objects.exists() else 0
        context['account_balance'] = AccountBalance.get_total_balance()
        context['expenses_today'] = self.get_expenses_today()
        return context

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        source = form.cleaned_data['budget_source']
        destination = form.cleaned_data['vendor']
        description = form.cleaned_data['description']
        category = form.cleaned_data['category']

        if source == 'ACC':
            try:
                account = AccountBalance.objects.get(pk=form.cleaned_data['account_pk'])
                if account.balance < amount:
                    form.add_error("amount", "The selected account does not have enough funds.")
                    return self.form_invalid(form)
            except AccountBalance.DoesNotExist:
                form.add_error("budget_source", "Selected account does not exist.")
                return self.form_invalid(form)

        else:
            cash = CashInHand.objects.first()
            if not cash:
                form.add_error("budget_source", "Cash in hand record not found.")
                return self.form_invalid(form)
            if cash.balance < amount:
                form.add_error("amount", "Not enough cash in hand.")
                return self.form_invalid(form)

        success, message = create_journal_expense_calculations(category=category, reason=description,
                                                               destination=destination.pk if destination else None,
                                                               amount=amount, source=source,
                                                               account_pk=account.pk if source == 'ACC' else None)
        if not success:
            form.add_error('budget_source', message)
            return self.form_invalid(form)

        messages.success(self.request, "Journal expense has been successfully created!")
        return super().form_valid(form)

    def get_expenses_today(self):
        today = date.today()
        expenses_today = JournalExpense.objects.filter(
            created_at__year=today.year,
            created_at__month=today.month,
            created_at__day=today.day
        )
        return sum(expense.amount for expense in expenses_today)
