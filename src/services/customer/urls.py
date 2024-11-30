from django.urls import path

from .views import (
    CustomerView, CustomerCreateView, CustomerDetailView, BillingAddressAddView, BillingAddressUpdateView,
    CustomerUpdateView, CustomerDeleteView
)

app_name = 'customer'
urlpatterns = [
    path('', CustomerView.as_view(), name='index'),
    path('create/', CustomerCreateView.as_view(), name='create'),
    path('<str:pk>/', CustomerUpdateView.as_view(), name='update'),
    path('detail/<int:pk>/', CustomerDetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', CustomerDeleteView.as_view(), name='delete'),


    path('billing-address-add/<int:pk>/', BillingAddressAddView.as_view(), name='billing-add'),
    path('billing-address-update/<int:pk>/', BillingAddressUpdateView.as_view(), name='billing-update'),

]
