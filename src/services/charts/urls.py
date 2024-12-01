from django.urls import path
from .views import ChartsIndex, generate_project_report, generate_monthly_report, download_journal, \
    generate_bank_statements_view

app_name = 'charts'

urlpatterns = [
    path('', ChartsIndex.as_view(), name='list'),
    path('generate/<str:pk>/', generate_project_report, name='generate'),
    path('charts/generate/<int:month>/<int:year>/', generate_monthly_report, name='generate_monthly_report'),
    path('download/<str:pk>/', download_journal, name='download'),
    path("generate-bank-statements/", generate_bank_statements_view, name="generate_bank_statements"),

]