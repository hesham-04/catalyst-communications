from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    FormView,
    UpdateView,
    DeleteView,
)

from src.services.assets.models import CashInHand, AccountBalance
from src.services.expense.views import Expense
from .bll import add_budget_to_project, add_cash_to_project
from .forms import AddBudgetForm, CreateProjectCashForm
from .forms import ProjectForm
from .models import Project
from ..customer.forms import CustomerForm
from ..invoice.models import Invoice, InvoiceItem
from ..loan.models import Loan
from ..quotation.models import Quotation
from ..transaction.models import Ledger
from ...web.dashboard.utils import get_monthly_income_expense


class ProjectView(LoginRequiredMixin, TemplateView):
    template_name = "project/project_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", "").strip()

        projects = Project.objects.all().order_by("-created_at")
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
        context["receivables"] = Invoice.calculate_total_received(
            project_id=kwargs["pk"]
        )
        return context


# VALIDATION ✔
class AddBudgetView(LoginRequiredMixin, FormView):
    template_name = "project/add_budget.html"
    form_class = AddBudgetForm

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project

        cih = CashInHand.objects.first().balance if CashInHand.objects.exists() else 0
        ab = AccountBalance.get_total_balance()

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

        add_budget_to_project(
            project_id=self.project.pk,
            amount=amount,
            source=source,
            reason=reason,
        )

        messages.success(
            self.request, f"{amount}PKR Budget added to {self.project.project_name}."
        )
        return redirect("project:detail", pk=self.project.pk)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.capitalize()}: {error}")
        return super().form_invalid(form)


class StartProjectView(LoginRequiredMixin, View):
    """Automated view to create an invoice from a quotation."""

    def get(self, request, *args, **kwargs):
        # Fetch the quotation based on the pk passed in the URL
        quotation = get_object_or_404(Quotation, pk=self.kwargs["pk"])

        # Create the invoice using the quotation details
        invoice = Invoice.objects.create(
            client_name=quotation.client_name,
            company_name=quotation.company_name,
            phone=quotation.phone,
            email=quotation.email,
            address=quotation.address,
            subject=quotation.subject,
            notes=quotation.notes,
            total_amount=quotation.total_amount,
            total_in_words=quotation.total_in_words,
            due_date=quotation.due_date,
            project=quotation.project,
            letterhead=quotation.letterhead,
            tax=quotation.tax,
            status="PENDING",
        )

        # Copy quotation items to invoice items
        for item in quotation.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                item_name=item.item_name,
                description=item.description,
                quantity=item.quantity,
                rate=item.rate,
                tax=item.tax,
                amount=item.amount,
            )

        # After saving all invoice items, recalculate the total for the invoice
        invoice.calculate_total_amount()
        project = get_object_or_404(Project, pk=quotation.project.pk)
        project.project_status = Project.ProjectStatus.IN_PROGRESS
        project.save()

        # Redirect to the invoice detail page after creation
        return redirect(reverse("project:detail", kwargs={"pk": project.pk}))


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
            "money_form_invoice": Invoice.calculate_total_received(
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

        if amount <= 0:
            form.add_error("amount", "The amount should be greater than zero.")
            return self.form_invalid(form)

        if amount > project.project_account_balance:
            form.add_error("amount", "Not enough balance in project budget")
            return self.form_invalid(form)

        add_cash_to_project(
            project_id=project.pk,
            amount=amount,
            reason=reason,
        )

        messages.success(self.request, "Worked like a charm")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = Project.objects.get(pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return reverse_lazy("project:finances", kwargs={"pk": self.kwargs["pk"]})


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


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "project/project_confirm_delete.html"
    success_url = reverse_lazy("project:index")
    context_object_name = "project"
