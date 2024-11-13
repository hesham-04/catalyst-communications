from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView

from src.services.project.models import Project
from .forms import LoanForm
from .forms import LoanReturnForm
from .models import Loan, LoanReturn


class LendLoanView(CreateView):
    form_class = LoanForm
    template_name = 'loan/lend_loan.html'

    def get_object(self):
        return get_object_or_404(Project, id=self.kwargs['pk'])

    def form_valid(self, form):
        loan = form.save(commit=False)
        loan.project = self.get_object()
        loan.save()
        self.get_object().adjust_budget(loan.loan_amount, 'LOAN', 'CREDIT')
        self.get_object().total_budget_assigned += loan.loan_amount
        messages.success(self.request, "Loan successfully assigned to project.")
        return redirect('project:detail', pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object()
        return context


class ReturnLoanView(CreateView):
    form_class = LoanReturnForm
    template_name = 'loan/return_loan.html'

    def get_object(self):
        return get_object_or_404(Loan, id=self.kwargs['pk'])

    def form_valid(self, form):
        loan = self.get_object()
        loan_return = form.save(commit=False)
        loan_return.loan = loan
        loan_return.save()

        loan.update_remaining_amount(loan_return.return_amount)
        messages.success(self.request, "Loan return successfully recorded.")
        return redirect('project:detail', pk=loan.project.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        context['loan'] = loan
        context['project'] = loan.project
        context['return_logs'] = LoanReturn.objects.filter(loan=loan).order_by('-return_date')
        return context
