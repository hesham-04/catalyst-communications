from django.urls import path

from .views import (
    ProjectView, ProjecCreateView, ProjectDetailView, AddBudgetView, StartProjectView, ProjectFinances, CreateProjectCash,
    ProjectUpdateView
)

app_name = 'project'
urlpatterns = [
    path('', ProjectView.as_view(), name='index'),
    path('create/', ProjecCreateView.as_view(), name='create'),
    path('detail/<int:pk>/', ProjectDetailView.as_view(), name='detail'),
    path('project/<int:pk>/start_project/', StartProjectView.as_view(), name='start_project'),
    path('<str:pk>/update/', ProjectUpdateView.as_view(), name='update'),

    path('transfer/<str:pk>/', CreateProjectCash.as_view(), name='transfer_to_cash'),
    path('project/<int:pk>/add_budget/', AddBudgetView.as_view(), name='add_budget'),

    path('finances/<str:pk>/', ProjectFinances.as_view(), name='finances')

]