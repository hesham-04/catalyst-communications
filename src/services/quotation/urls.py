from django.urls import path
from .views import CreateQuotationView, QuotationDetailView, QuotationUpdateView

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
