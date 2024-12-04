from django.urls import path
from .views import CustomLoginView, UserListView, CustomLogoutView
app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='users'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]