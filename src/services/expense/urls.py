from django.urls import path
from .views import (
    CreateExpenseView, ExpenseIndexView, ExpenseCreateView, ExpenseCategoryCreateView,
)

app_name = 'expense'
urlpatterns = [
    path('', ExpenseIndexView.as_view(), name='index'),
    path('create/<int:pk>/', CreateExpenseView.as_view(), name='create'),# project detail
    path('create/', ExpenseCreateView.as_view(), name='create-expense-home'),
    path('expense-category/create/', ExpenseCategoryCreateView.as_view(), name='expense-category-create'),
]
