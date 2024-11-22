from django.urls import path
from .views import (
    VendorListView, VendorDetailView, VendorCreateView
)
app_name = 'vendor'

urlpatterns = [
    path('', VendorListView.as_view(), name='vendors'),
    path('create/', VendorCreateView.as_view(), name='create'),
    path('<str:pk>/detail/', VendorDetailView.as_view(), name='detail'),
]