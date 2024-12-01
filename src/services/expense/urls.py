from django.urls import path
from .views import (
    CreateExpenseView, ExpenseIndexView, ExpenseCategoryCreateView, ExpensePaymentView,
    JournalExpenseCreateView, ExpenseCategoryListView
)

app_name = 'expense'
urlpatterns = [
    path('', ExpenseIndexView.as_view(), name='index'),
    path('create/<int:pk>/', CreateExpenseView.as_view(), name='create'),# project detail

    path('pay-expense/<int:pk>/', ExpensePaymentView.as_view(), name='pay-expense'),
    path('journal-create/', JournalExpenseCreateView.as_view(), name='journal-create'),
]

urlpatterns += [
    path('expense-category/create/', ExpenseCategoryCreateView.as_view(), name='expense-category-create'),
    path('categories/', ExpenseCategoryListView.as_view(), name='expense-category-list'),
]

