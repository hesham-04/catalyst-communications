from django.urls import path
from .views import ChartsIndex, generate_project_report, \
    generate_bank_statements_view, project_expenses

app_name = 'charts'

urlpatterns = [
    path('', ChartsIndex.as_view(), name='list'),
    path('generate/<str:pk>/', generate_project_report, name='project-report'),


    path('download/<str:pk>/', project_expenses, name='project-expense-journal'),
    path("generate-bank-statements/", generate_bank_statements_view, name="generate_bank_statements"),

]