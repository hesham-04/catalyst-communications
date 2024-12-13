from django.urls import path
from .views import CreateInvoiceView, InvoiceDetailView, InvoicePaidView

app_name = "invoice"

urlpatterns = [
    path(
        "project/<str:pk>/create-invoice/", CreateInvoiceView.as_view(), name="create"
    ),
    path("detail/<str:pk>/", InvoiceDetailView.as_view(), name="detail"),
    path("update/<str:pk>/", InvoicePaidView.as_view(), name="invoice-paid"),
]
