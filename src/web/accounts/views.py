from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from src.web.accounts.models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class UserListView(ListView):
    model = User

