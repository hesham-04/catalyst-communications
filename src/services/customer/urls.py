from django.urls import path

from .views import (
    CustomerView, CustomerCreateView
)

app_name = 'customer'

urlpatterns = [
    path('', CustomerView.as_view(), name='home'),
    path('create/', CustomerCreateView.as_view(), name='create'),
]