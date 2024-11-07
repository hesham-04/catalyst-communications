from django.urls import path

from .views import (
    LendLoanView, ReturnLoanView,
)

app_name = 'loan'
urlpatterns = [
    path('lend_loan/<int:pk>/', LendLoanView.as_view(), name='lend_loan'),
    path('return_loan/<int:pk>/', ReturnLoanView.as_view(), name='return_loan'),
]