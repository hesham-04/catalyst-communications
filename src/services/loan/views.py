from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView

from src.services.project.bll import add_loan_to_project
from src.services.project.bll import return_loan_to_lender
from src.services.project.models import Project
from .forms import LoanForm
from .forms import LoanReturnForm
from .models import Loan, LoanReturn, Lender


class LendLoanView(CreateView):
    form_class = LoanForm
    template_name = 'loan/lend_loan.html'

    def get_object(self):
        return get_object_or_404(Project, id=self.kwargs['pk'])

    def form_valid(self, form):
        loan = form.save(commit=False)
        lender = form.cleaned_data['lender']
        amount = form.cleaned_data['loan_amount']
        destination = form.cleaned_data['destination']
        reason = form.cleaned_data['reason']

        # Make changes to the Project & Ledger before creating the loan Object
        add_loan_to_project(
            project_id=self.kwargs['pk'],
            amount=amount,
            source=lender,
            destination=destination,
            reason=reason
        )

        # Link the project to loan object
        loan.project = self.get_object()
        loan.save()

        messages.success(self.request, "Loan successfully created for project.")
        return redirect('project:detail', pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object()
        return context


class LoanListView(ListView):
    model = Loan
    template_name = 'loan/loan_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, id=self.kwargs['pk'])
        return context

    def get_queryset(self):
        return Loan.objects.filter(project=self.kwargs['pk']).order_by('-due_date')


class ReturnLoanView(CreateView):
    form_class = LoanReturnForm
    template_name = 'loan/return_loan.html'

    def get_object(self):
        return get_object_or_404(Loan, id=self.kwargs['pk'])

    def form_valid(self, form):
        loan = self.get_object()
        loan_return = form.save(commit=False)

        return_amount = form.cleaned_data['return_amount']
        remarks = form.cleaned_data['remarks']
        source = form.cleaned_data['source']

        # Create an expense Object for this project.
        # Subtract from the Loan model.

        return_loan_to_lender(
            loan_id=loan.pk,
            project_id=loan.project.id,
            amount=return_amount,
            source=source,
            destination=loan.lender.name,
            reason=remarks
        )

        loan_return.loan = loan
        loan_return.save()
        messages.success(self.request, "Loan return successfully recorded.")
        return redirect('project:detail', pk=loan.project.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        context['loan'] = loan
        context['project'] = loan.project
        context['return_logs'] = LoanReturn.objects.filter(loan=loan).order_by('-return_date')
        return context


class LenderListView(ListView):
    model = Lender


class LenderDetailView(DetailView):
    model = Lender

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loans'] = self.object.loans.all()
        return context
