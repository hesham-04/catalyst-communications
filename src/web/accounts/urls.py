from django.urls import path
from .views import (
    CustomLoginView,
    UserListView,
    CustomLogoutView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="list"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]

urlpatterns += [
    path("create/", UserCreateView.as_view(), name="create"),
    path("<str:pk>/update/", UserUpdateView.as_view(), name="update"),
    path("<str:pk>/delete/", UserDeleteView.as_view(), name="delete"),
]
