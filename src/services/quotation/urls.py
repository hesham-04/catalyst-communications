from django.urls import path
from . views import CreateQuotationView, PrintQuotationView

app_name = 'quotation'

urlpatterns = [
    path('project/<int:pk>/create-quotation/', CreateQuotationView.as_view(), name='create_quotation'),
    path('print/<int:pk>/', PrintQuotationView.as_view(), name='print'),
]