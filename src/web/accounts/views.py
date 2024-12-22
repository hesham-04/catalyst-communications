from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import User
from .forms import UserForm, UserUpdateForm
from ...core.mixins import AdminRequiredMixin


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("accounts:login")


class UserListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    model = User


class UserCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:list")


class UserUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:list")


class UserDeleteView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:list")
