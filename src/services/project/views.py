from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, RedirectView, FormView, UpdateView

from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.views import Expense
from .bll import add_budget_to_project
from .forms import AddBudgetForm, CreateProjectCashForm
from .forms import ProjectForm
from .models import Project
from ..invoice.models import Invoice
from ..transaction.models import Ledger

from django.core.paginator import Paginator
from django.db.models import Q


class ProjectView(TemplateView):
    template_name = 'project/project_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('q', '').strip()

        projects = Project.objects.all()
        if search_query:
            projects = projects.filter(
                Q(project_name__icontains=search_query)
            )

        paginator = Paginator(projects, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['projects'] = page_obj
        context['search_query'] = search_query
        return context


class ProjectUpdateView(UpdateView):
    model = Project
    fields = ['project_name', 'description']



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

        visible_transaction_types = [
            ('BUDGET_ASSIGN', 'Budget Assigned to Project'),
            ('CREATE_EXPENSE', 'Expense Created'),
            ('PAY_EXPENSE', 'Expense Paid'),
            ('INVOICE_PAYMENT', 'Invoice Paid'),
            ('CREATE_LOAN', 'Loan Created'),
            ('RETURN_LOAN', 'Loan Returned'),
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
            "transaction_types": visible_transaction_types,
            "selected_transaction_type": transaction_filter,
            'budget_assigned': total_budget_assigned,
            'money_form_invoice': Invoice.calculate_total_receieved(project_id=project.pk),
            'Project_expenditure': Expense.calculate_total_expenses(project_id=project.pk)
        }
        return render(request, self.template_name, context)


class CreateProjectCash(FormView):
    form_class = CreateProjectCashForm
    template_name = 'project/create_project_cash.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        project = Project.objects.get(pk=pk)
        form = self.form_class()
        return self.render_to_response({'form': form, 'project': project})

    def form_valid(self, form):
        print()
        project = Project.objects.get(pk=self.kwargs['pk'])
        amount = form.cleaned_data.get('amount')
        reason = form.cleaned_data.get('reason')

        if amount > project.project_account_balance:
            form.add_error('amount', "Not enough balance in project budget")
            return self.form_invalid(form)

        project.project_cash += amount
        project.project_account_balance -= amount

        project.save()

        Ledger.objects.create(
            transaction_type="TRANSFER",
            project=project,
            amount=amount,
            source=f"Project {project.project_name} ACC ({project.pk})",
            destination=f"Project {project.project_name} CASH ({project.pk})",
            reason=reason,
        )

        messages.success(self.request, "Worked like a charm")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project:detail', kwargs={'pk': self.kwargs.pk})
