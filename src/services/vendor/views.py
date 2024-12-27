from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DetailView, ListView

from .forms import VendorForm
from .models import Vendor
from ..expense.models import Expense, ExpenseCategory
from ..project.models import Project
from ...web.dashboard.utils import ledger_filter


# Create your views here.
class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    success_url = reverse_lazy("vendor:vendors")  # Redirect after creation


class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    paginate_by = 25
    context_object_name = "vendors"

    def get_queryset(self):
        queryset = Vendor.objects.all().order_by("-created_at")

        order = self.request.GET.get("order", None)
        if order == "desc":
            queryset = queryset.order_by("-total_expense")

        return queryset


class VendorDetailView(LoginRequiredMixin, DetailView):
    model = Vendor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        expenses = ledger_filter(
            "MISC_EXPENSE", destination=self.object
        ) | ledger_filter("CREATE_EXPENSE", destination=self.object)

        project_id = self.request.GET.get("project")
        category_id = self.request.GET.get("category")
        payment_status = self.request.GET.get("status")

        if project_id:
            expenses = expenses.filter(project_id=project_id)
        if category_id:
            expenses = expenses.filter(expense_category_id=category_id)
        if payment_status:
            expenses = expenses.filter(payment_status=payment_status)

        # Add the filtered expenses to the context
        context["expenses"] = expenses

        # Add additional context for the filter options (dropdowns in the template)
        context["projects"] = (
            Project.objects.all()
        )  # Filters the projects that have expenses with this vendor
        context["categories"] = ExpenseCategory.objects.all()
        context["statuses"] = Expense.PaymentStatus.choices

        return context
