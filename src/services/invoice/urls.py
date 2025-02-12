from django.urls import path
from .views import (
    CreateInvoiceView,
    InvoiceDetailView,
    InvoicePaidView,
    InvoiceDeleteView,
    InvoiceUpdateView,
    UpdateInvoiceView, DeliveryChallanView,
)

app_name = "invoice"

urlpatterns = [
    path(
        "project/<str:pk>/create-invoice/", CreateInvoiceView.as_view(), name="create"
    ),
    path("detail/<str:pk>/", InvoiceDetailView.as_view(), name="detail"),
    path("paid/<str:pk>/", InvoicePaidView.as_view(), name="invoice-paid"),
    path("delete/<str:pk>/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("edit/<str:pk>/", InvoiceUpdateView.as_view(), name="invoice-edit"),
    path("update/<str:pk>/", UpdateInvoiceView.as_view(), name="invoice-update"),
    path("challan/<int:invoice_id>/", DeliveryChallanView.as_view(), name="generate_challan"),

]
