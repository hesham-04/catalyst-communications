from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, CashInHand, AccountBalance
from .forms import AddBudgetForm
from .forms import ProjectForm


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
        return context




def add_budget(request, pk):
    project = get_object_or_404(Project, id=pk)
    cash_balance = CashInHand.objects.first().balance
    account_balance = AccountBalance.objects.first().balance
    client_funds = project.client_funds_received

    if request.method == 'POST':
        form = AddBudgetForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            source = form.cleaned_data['source']
            transaction_type = form.cleaned_data['transaction_type']

            # Adjust balances and project budget
            project.adjust_budget(amount, source, transaction_type)
            messages.success(request, "Budget successfully updated.")
            return redirect('project:detail', pk=pk)
    else:
        form = AddBudgetForm()

    context = {
        'project': project,
        'form': form,
        'cash_balance': cash_balance,
        'account_balance': account_balance,
        'client_funds': client_funds,
    }
    return render(request, 'project/add_budget.html', context)


