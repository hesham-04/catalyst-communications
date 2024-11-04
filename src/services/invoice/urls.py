from django.urls import path

from .views import (
    InvoiceView
)

app_name = 'invoice'

urlpatterns = [
    path('', InvoiceView.as_view(), name='home'),
]
