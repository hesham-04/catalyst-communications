from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    RedirectView,
    FormView,
    UpdateView,
)

from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.views import Expense
from .bll import add_budget_to_project
from .forms import AddBudgetForm, CreateProjectCashForm
from .forms import ProjectForm
from .models import Project
from django.http import JsonResponse
from ..customer.forms import CustomerForm
from ..customer.models import Customer
from ..invoice.models import Invoice
from ..loan.models import Loan
from ..transaction.models import Ledger
from ...web.dashboard.utils import get_monthly_income_expense


class ProjectView(LoginRequiredMixin, TemplateView):
    template_name = "project/project_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", "").strip()

        projects = Project.objects.all()
        if search_query:
            projects = projects.filter(Q(project_name__icontains=search_query))

        paginator = Paginator(projects, 20)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["projects"] = page_obj
        context["search_query"] = search_query
        return context


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ["project_name", "description"]

    def get_success_url(self):
        return reverse_lazy("project:detail", kwargs={"pk": self.object.pk})


class ProjectCreateView(LoginRequiredMixin, CreateView):
    template_name = "project/project_form.html"
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy("project:index")

    def form_valid(self, form):
        name = form.cleaned_data.get("project_name")

        if name.isdigit():
            form.add_error(
                "project_name", "This field cannot be a purely numeric value."
            )
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("project:detail", kwargs={"pk": self.object.pk})


# views.py

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.template.loader import render_to_string


class ModalCustomerCreateView(View):
    def get(self, request):
        form = CustomerForm()
        return JsonResponse(
            {
                "success": True,
                "form_html": render_to_string(
                    "project/customer_form_modal.html", {"form": form}
                ),
            }
        )

    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            print("-=====================================")
            customer = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "customer": {
                        "id": customer.id,
                        "first_name": customer.first_name,
                        "last_name": customer.last_name,
                    },
                }
            )
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        print("NO")
        return JsonResponse({"success": False, "errors": form.errors})


class ProjectDetailView(LoginRequiredMixin, TemplateView):
    template_name = "project/project_detail.html"

    def get_context_data(self, **kwargs):
        income, expense = get_monthly_income_expense(project_id=kwargs["pk"])
        context = super().get_context_data(**kwargs)
        context["income"] = income
        context["expense"] = expense
        context["project"] = Project.objects.get(pk=kwargs["pk"])
        context["total_expenses"] = Expense.calculate_total_expenses(
            project_id=kwargs["pk"]
        )
        context["payable"] = Loan.calculate_total_unpaid_amount(project_pk=kwargs["pk"])
        context["receivables"] = Invoice.calculate_total_receieved(
            project_id=kwargs["pk"]
        )
        return context


class AddBudgetView(LoginRequiredMixin, FormView):
    template_name = "project/add_budget.html"
    form_class = AddBudgetForm

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project

        if CashInHand.objects.first():
            cih = CashInHand.objects.first().balance
        else:
            cih = 0

        if AccountBalance.objects.first():
            ab = AccountBalance.objects.first().balance
        else:
            ab = 0

        context["cash_balance"] = cih
        context["account_balance"] = ab
        return context

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        source = form.cleaned_data["source"]
        reason = form.cleaned_data["reason"]

        if amount <= 0:
            form.add_error("amount", "Amount cannot be zero.")
            return self.form_invalid(form)

        if AccountBalance.objects.get(pk=source.pk).balance < amount:
            form.add_error("source", "The selected Account does not have enough Funds.")
            return self.form_invalid(form)

        if source == "ACC":
            # account = AccountBalance.objects.get(id=source.id)  # FOR LATER
            account = AccountBalance.objects.first()
            if account.balance < amount:
                form.add_error("amount", "Insufficient balance in the account.")
                return self.form_invalid(form)

        add_budget_to_project(
            project_id=self.project.pk,
            amount=amount,
            source=source,
            destination=None,
            reason=reason,
        )

        messages.success(self.request, "Budget successfully updated.")

        return redirect("project:detail", pk=self.project.pk)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission.")
        return super().form_invalid(form)


class StartProjectView(LoginRequiredMixin, RedirectView):
    """A view that changes the project status to in progress and redirects to the project detail page"""

    def get_redirect_url(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs["pk"])
        project.project_status = Project.ProjectStatus.IN_PROGRESS
        project.save()
        return reverse("project:detail", kwargs={"pk": project.pk})


class ProjectFinances(LoginRequiredMixin, View):
    template_name = "project/finances.html"

    def get(self, request, pk):
        project = Project.objects.get(pk=pk)

        transaction_filter = request.GET.get("transaction_type", None)

        ledger_entries = Ledger.objects.filter(project_id=project.pk)

        if transaction_filter:
            ledger_entries = ledger_entries.filter(transaction_type=transaction_filter)

        visible_transaction_types = [
            ("BUDGET_ASSIGN", "Budget Assigned to Project"),
            ("CREATE_EXPENSE", "Expense Created"),
            ("INVOICE_PAYMENT", "Invoice Paid"),
            ("TRANSFER", "Funds Transfer"),  # Only from Project ACC to Project CASH
            ("CREATE_LOAN", "Loan Created"),
            ("RETURN_LOAN", "Loan Returned"),
        ]

        budget_assign_transactions = Ledger.objects.filter(
            project_id=project.pk, transaction_type="BUDGET_ASSIGN"
        )

        total_budget_assigned = (
            budget_assign_transactions.aggregate(Sum("amount"))["amount__sum"] or 0
        )

        Expense.calculate_total_expenses(project_id=project.pk)

        context = {
            "project": project,
            "ledger_entries": ledger_entries,
            "transaction_types": visible_transaction_types,
            "selected_transaction_type": transaction_filter,
            "budget_assigned": total_budget_assigned,
            "money_form_invoice": Invoice.calculate_total_receieved(
                project_id=project.pk
            ),
            "invoice_receivables": Invoice.calculate_total_receivables(
                project_id=project.pk
            ),
            "project_expenditure": Expense.calculate_total_expenses(
                project_id=project.pk
            ),
            "loans": Loan.calculate_total_unpaid_amount(project_pk=project.pk),
        }
        return render(request, self.template_name, context)


class CreateProjectCash(LoginRequiredMixin, FormView):
    form_class = CreateProjectCashForm
    template_name = "project/create_project_cash.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        project = Project.objects.get(pk=pk)
        form = self.form_class()
        return self.render_to_response({"form": form, "project": project})

    def form_valid(self, form):
        print()
        project = Project.objects.get(pk=self.kwargs["pk"])
        amount = form.cleaned_data.get("amount")
        reason = form.cleaned_data.get("reason")

        if amount > project.project_account_balance:
            form.add_error("amount", "Not enough balance in project budget")
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
        return reverse_lazy("project:finances", kwargs={"pk": self.kwargs.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = Project.objects.get(pk=self.kwargs["pk"])
        return context


class ProjectExpensesView(LoginRequiredMixin, TemplateView):
    template_name = "project/project_expenses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_list = Ledger.objects.filter(
            Q(transaction_type="CREATE_EXPENSE") | Q(transaction_type="RETURN_LOAN"),
            project_id=self.kwargs["pk"],
        )
        project = Project.objects.get(pk=self.kwargs["pk"])

        paginator = Paginator(object_list, 20)
        page = self.request.GET.get("page")
        paginated_object_list = paginator.get_page(page)

        context["object_list"] = paginated_object_list
        context["project"] = project
        return context


class ProjectInvoiceView(LoginRequiredMixin, TemplateView):
    template_name = "project/project_invoice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_list = Invoice.objects.filter(project=self.kwargs["pk"])
        _project = Project.objects.get(pk=self.kwargs["pk"])

        paginator = Paginator(object_list, 20)
        page = self.request.GET.get("page")
        paginated_object_list = paginator.get_page(page)

        context["object_list"] = paginated_object_list
        context["project"] = _project
        return context
