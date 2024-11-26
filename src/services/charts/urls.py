from django.urls import path
from .views import ChartsIndex, export_project_to_excel

app_name = 'charts'

urlpatterns = [
    path('', ChartsIndex.as_view(), name='list'),
    path('geneerate<str:pk>/', export_project_to_excel, name='generate')
]