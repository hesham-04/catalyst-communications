from django.urls import path

from .forms import MiscLoanReturnForm
from .views import (
    LendLoanView, ReturnLoanView, LoanListView, LenderListView, LenderDetailView, LenderCreateView, MiscLoanCreateView,
    MiscLoanReturnView, LenderDeleteView
)

app_name = 'loan'
urlpatterns = [
    path('list/<int:pk>/', LoanListView.as_view(), name='list'),
    path('lend-loan/<int:pk>/', LendLoanView.as_view(), name='lend_loan'),
    path('return-loan/<int:pk>/', ReturnLoanView.as_view(), name='return_loan'),


    path('lender/', LenderListView.as_view(), name='lenders'),
    path('lender/create/', LenderCreateView.as_view(), name='lender-create'),
    path('lender/<str:pk>/', LenderDetailView.as_view(), name='lender-detail'),

    path('lend-misc-loan/<str:pk>/', MiscLoanCreateView.as_view(), name='lend-misc-loan'),
    path('return-misc-loan/<str:pk>/', MiscLoanReturnView.as_view(), name='return-misc-loan'),

    path('lender-delete/<str:pk>/', LenderDeleteView.as_view(), name='lender-delete'),

]