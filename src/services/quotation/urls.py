from django.urls import path
from .views import (
    CreateQuotationView,
    QuotationDetailView,
    QuotationUpdateView,
    GeneralView,
    CreateGeneralQuotationView,
    GeneralQuotationDetailView,
    invoice_gen_quote,
)
from ..invoice.views import InvoicePaidView

app_name = "quotation"

urlpatterns = [
    path(
        "project/<int:pk>/create-quotation/",
        CreateQuotationView.as_view(),
        name="create_quotation",
    ),
    path("detail/<int:pk>/", QuotationDetailView.as_view(), name="detail"),
    path("<str:pk>/edit/", QuotationUpdateView.as_view(), name="edit"),
]


urlpatterns += [
    path("general/", GeneralView.as_view(), name="open-market"),
    path(
        "create-general-quotation/",
        CreateGeneralQuotationView.as_view(),
        name="create_general_quotation",
    ),
    path(
        "general-detail/<int:pk>/",
        GeneralQuotationDetailView.as_view(),
        name="general_detail",
    ),
    path("invoice-gen-quote/<str:pk>", invoice_gen_quote, name="invoice_gen_quote"),
    path(
        "quotation/<int:pk>/paid/",
        InvoicePaidView.as_view(),
        {"q": True},
        name="quotation_paid",
    ),
]
