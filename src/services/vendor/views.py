from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DetailView, ListView
from .models import (
    Vendor
)
from .forms import VendorForm
from ..expense.models import Expense, ExpenseCategory
from ..project.models import Project


# Create your views here.
class VendorCreateView(CreateView):
    model = Vendor
    form_class = VendorForm
    success_url = reverse_lazy('expense:index')  # Redirect after creation

class VendorListView(ListView):
    model = Vendor
    paginate_by = 100

from django.db.models import Q

class VendorDetailView(DetailView):
    model = Vendor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Base queryset: Expenses linked to this vendor
        expenses = Expense.objects.filter(vendor=self.object)

        # Extract filter parameters from the request
        project_id = self.request.GET.get('project')  # Project filter
        category_id = self.request.GET.get('category')  # Expense Category filter
        payment_status = self.request.GET.get('status')  # Payment status filter (PAID/UNPAID)

        # Apply filters dynamically if parameters are present
        if project_id:
            expenses = expenses.filter(project_id=project_id)
        if category_id:
            expenses = expenses.filter(category_id=category_id)
        if payment_status:
            expenses = expenses.filter(payment_status=payment_status)

        # Add the filtered expenses to the context
        context['expenses'] = expenses

        # Add additional context for the filter options (dropdowns in the template)
        context['projects'] = Project.objects.filter(expenses__vendor=self.object).distinct()
        context['categories'] = ExpenseCategory.objects.all()
        context['statuses'] = Expense.PaymentStatus.choices

        return context
