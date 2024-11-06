from django.urls import path

from .views import (
    ProjectView, ProjecCreateView, ProjectDetailView, add_budget
)

app_name = 'project'
urlpatterns = [
    path('', ProjectView.as_view(), name='index'),
    path('create/', ProjecCreateView.as_view(), name='create'),
    path('detail/<int:pk>/', ProjectDetailView.as_view(), name='detail'),
    path('project/<int:pk>/add_budget/', add_budget, name='add_budget'),

]