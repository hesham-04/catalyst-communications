from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, RedirectView, FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, CashInHand, AccountBalance
from .forms import AddBudgetForm
from .forms import ProjectForm
from src.services.expense.views import Expense
from ..invoice.models import Invoice
from .bll import add_budget_to_project


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
        context['receivables'] = Invoice.calculate_total_receivables(project_id=kwargs['pk'])
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
        destination = form.cleaned_data['destination']
        reason = form.cleaned_data['reason']

        add_budget_to_project(
            project_id=self.project.pk,
            amount=amount,
            source=source,
            destination=destination,
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







