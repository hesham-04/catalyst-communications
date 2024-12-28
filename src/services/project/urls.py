from django.urls import path

from .views import (
    ProjectView,
    ProjectCreateView,
    ProjectDetailView,
    AddBudgetView,
    StartProjectView,
    ProjectFinances,
    CreateProjectCash,
    ProjectUpdateView,
    ProjectExpensesView,
    ProjectInvoiceView,
    ModalCustomerCreateView,
    ProjectDeleteView,
)

app_name = "project"
urlpatterns = [
    path("", ProjectView.as_view(), name="index"),
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<str:pk>/detail/", ProjectDetailView.as_view(), name="detail"),
    path("<str:pk>/start-project/", StartProjectView.as_view(), name="start_project"),
    path("<str:pk>/update/", ProjectUpdateView.as_view(), name="update"),
    path("<str:pk>/transfer/", CreateProjectCash.as_view(), name="transfer_to_cash"),
    path("<str:pk>/add-budget/", AddBudgetView.as_view(), name="add_budget"),
    path("<str:pk>/expenses/", ProjectExpensesView.as_view(), name="expenses"),
    path("<str:pk>/invoices/", ProjectInvoiceView.as_view(), name="invoices"),
    path("<str:pk>/finances/", ProjectFinances.as_view(), name="finances"),
    path("<str:pk>/delete/", ProjectDeleteView.as_view(), name="delete"),
]

urlpatterns += [
    path(
        "customer/modal-create/",
        ModalCustomerCreateView.as_view(),
        name="customer_modal_create",
    ),
]
