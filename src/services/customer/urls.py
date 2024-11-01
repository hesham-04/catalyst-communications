from django.urls import path

from .views import (
    CustomerView, CustomerCreateView, CustomerDetailView
)

app_name = 'customer'

urlpatterns = [
    path('', CustomerView.as_view(), name='home'),
    path('create/', CustomerCreateView.as_view(), name='create'),
    path('detail/<int:pk>/', CustomerDetailView.as_view(), name='detail'),
]