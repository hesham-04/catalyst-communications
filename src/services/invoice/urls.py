from django.urls import path
from .views import CreateInvoiceView, PrintInvoiceView, InvoiceDetailView, InvoicePaidView

app_name = 'invoice'

urlpatterns = [
    path('project/<int:pk>/create-invoice/', CreateInvoiceView.as_view(), name='create'),
    path('print/<int:pk>/', PrintInvoiceView.as_view(), name='print'), # Unused (DISCARD UPON PROJECT COMPLETION )
    path('detail/<int:pk>/', InvoiceDetailView.as_view(), name='detail'),


    path('update/<str:pk>/', InvoicePaidView.as_view(), name='invoice-paid')
]
