from django.urls import path
from .views import CreateQuotationView, PrintQuotationView, QuotationDetailView

app_name = "quotation"

urlpatterns = [
    path(
        "project/<int:pk>/create-quotation/",
        CreateQuotationView.as_view(),
        name="create_quotation",
    ),
    path("detail/<int:pk>/", QuotationDetailView.as_view(), name="detail"),
]
