from django.urls import path
from .views import ChartsIndex, export_project_to_excel, generate_monthly_report, download_journal

app_name = 'charts'

urlpatterns = [
    path('', ChartsIndex.as_view(), name='list'),
    path('geneerate<str:pk>/', export_project_to_excel, name='generate'),
    path('charts/generate/<int:month>/<int:year>/', generate_monthly_report, name='generate_monthly_report'),
    path('download/<str:pk>/', download_journal, name='download'),
]