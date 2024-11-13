from django.urls import path
from .views import CreateInvoiceView, PrintInvoiceView

app_name = 'invoice'

urlpatterns = [
    path('project/<int:pk>/create-invoice/', CreateInvoiceView.as_view(), name='create'),
    path('print/<int:pk>/', PrintInvoiceView.as_view(), name='print'),
]
