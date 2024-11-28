from django.db.models import Sum
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, RedirectView, FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, CashInHand, AccountBalance
from .forms import AddBudgetForm
from .forms import ProjectForm
from src.services.expense.views import Expense
from ..invoice.models import Invoice
from .bll import add_budget_to_project
from ..transaction.models import Ledger


class ProjectView(TemplateView):
    template_name = 'project/project_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        return context


class ProjecCreateView(CreateView):
    template_name = 'project/project_form.html'
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy('project:index')

    def get_success_url(self):
        return reverse_lazy('project:detail', kwargs={'pk': self.object.pk})



class ProjectDetailView(TemplateView):
    template_name = 'project/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=kwargs['pk'])
        context['total_expenses'] = Expense.calculate_total_expenses(project_id=kwargs['pk'])
        context['payable'] = Expense.calculate_total_expenses(project_id=kwargs['pk'])
        context['receivables'] = Invoice.calculate_total_receieved(project_id=kwargs['pk'])
        return context


class AddBudgetView(FormView):
    template_name = 'project/add_budget.html'
    form_class = AddBudgetForm

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project

        if CashInHand.objects.first():
            cih = CashInHand.objects.first().balance
        else:
            cih = 0

        if AccountBalance.objects.first():
            ab = AccountBalance.objects.first().balance
        else:
            ab = 0

        context['cash_balance'] = cih
        context['account_balance'] = ab
        return context

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        source = form.cleaned_data['source']
        reason = form.cleaned_data['reason']

        if amount <= 0:
            form.add_error('amount', "Amount cannot be zero.")
            return self.form_invalid(form)

        if AccountBalance.objects.get(pk=source.pk).balance < amount:
            form.add_error('source', "The selected Account does not have enough Funds.")
            return self.form_invalid(form)

        if source == 'ACC':
            # account = AccountBalance.objects.get(id=source.id)  # FOR LATER
            account = AccountBalance.objects.first()
            if account.balance < amount:
                form.add_error('amount', 'Insufficient balance in the account.')
                return self.form_invalid(form)

        add_budget_to_project(
            project_id=self.project.pk,
            amount=amount,
            source=source,
            destination=None,
            reason=reason
        )

        messages.success(self.request, "Budget successfully updated.")

        return redirect('project:detail', pk=self.project.pk)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission.")
        return super().form_invalid(form)

class StartProjectView(RedirectView):
    """A view that changes the project status to in progress and redirects to the project detail page"""
    def get_redirect_url(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        project.project_status = Project.ProjectStatus.IN_PROGRESS
        project.save()
        return reverse('project:detail', kwargs={'pk': project.pk})



class ProjectFinances(View):
    template_name = 'project/finances.html'

    def get(self, request, pk):
        project = Project.objects.get(pk=pk)

        transaction_filter = request.GET.get('transaction_type', None)

        ledger_entries = Ledger.objects.filter(project_id=project.pk)

        if transaction_filter:
            ledger_entries = ledger_entries.filter(transaction_type=transaction_filter)

        totals_by_type = {
            transaction[0]: ledger_entries.filter(transaction_type=transaction[0]).aggregate(Sum('amount'))['amount__sum']
            for transaction in Ledger.TRANSACTION_TYPES
        }

        visible_transaction_types = [
            ('BUDGET_ASSIGN', 'Budget Assigned to Project'),
            ('CREATE_EXPENSE', 'Expense Created'),
            ('PAY_EXPENSE', 'Expense Paid'),
            ('INVOICE_PAYMENT', 'Invoice Paid')
        ]

        budget_assign_transactions = Ledger.objects.filter(
            project_id=project.pk,
            transaction_type='BUDGET_ASSIGN'
        )

        budget_from_invoice = Invoice.objects.filter(status='PAID')
        total_budget_assigned = budget_assign_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        Expense.calculate_total_expenses(project_id=project.pk)

        context = {
            "project": project,
            "ledger_entries": ledger_entries,
            "totals_by_type": totals_by_type,
            "transaction_types": visible_transaction_types,
            "selected_transaction_type": transaction_filter,
            'budget_assigned': total_budget_assigned,
            'money_form_invoice': Invoice.calculate_total_receieved(project_id=project.pk),
            'Project_expenditure': Expense.calculate_total_expenses(project_id=project.pk)
        }
        return render(request, self.template_name, context)
