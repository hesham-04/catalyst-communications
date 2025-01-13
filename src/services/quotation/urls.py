from django.urls import path
from .views import (
    CreateQuotationView,
    QuotationDetailView,
    QuotationUpdateView,
    GeneralView,
    CreateGeneralQuotationView,
    GeneralQuotationDetailView,
    invoice_gen_quote,
    UpdateQuotationView,
    UpdateGeneralQuotationView,
    GeneralQuotationUpdateView,
    GeneralQuotationDeleteView
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
    path(
        "<str:pk>/edit/", QuotationUpdateView.as_view(), name="edit"
    ),  # only the model
    path(
        "<str:pk>/update/", UpdateQuotationView.as_view(), name="update"
    ),  # detailed with formsets
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
    path(
        "general/update/<str:pk>/",
        UpdateGeneralQuotationView.as_view(),
        name="general_update",
    ),
    path(
        "general/<str:pk>/edit/",
        GeneralQuotationUpdateView.as_view(),
        name="general_edit",
    ),  # only the model
    path('<str:pk>/delete/', GeneralQuotationDeleteView.as_view(), name='general-delete'),
]
