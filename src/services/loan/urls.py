from django.urls import path

from .views import (
    LendLoanView, ReturnLoanView, LoanListView
)

app_name = 'loan'
urlpatterns = [
    path('list/<int:pk>/', LoanListView.as_view(), name='list'),
    path('lend_loan/<int:pk>/', LendLoanView.as_view(), name='lend_loan'),
    path('return_loan/<int:pk>/', ReturnLoanView.as_view(), name='return_loan'),
]