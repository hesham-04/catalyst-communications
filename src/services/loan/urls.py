from django.urls import path

from .views import (
    LendLoanView, ReturnLoanView, LoanListView, LenderListView,LenderDetailView, LenderCreateView
)

app_name = 'loan'
urlpatterns = [
    path('list/<int:pk>/', LoanListView.as_view(), name='list'),
    path('lend_loan/<int:pk>/', LendLoanView.as_view(), name='lend_loan'),
    path('return_loan/<int:pk>/', ReturnLoanView.as_view(), name='return_loan'),


    path('lender/', LenderListView.as_view(), name='lenders'),
    path('lender/create/', LenderCreateView.as_view(), name='lender-create'),
    path('lender/<str:pk>/', LenderDetailView.as_view(), name='lender-detail'),

]