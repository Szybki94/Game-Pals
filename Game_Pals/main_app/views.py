from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import (
    login_required,
)
from .forms import LoginForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


# Create your views here.
class TEST(View):
    def get(self, request):
        return render(request, "test.html", {})


class HomeView(View):
    def get(self, request):
        return render(request, "test.html", {})


class LoginView(View):
    def get(self, request):
        ctx = {}
        ctx['form'] = LoginForm
        return render(request, "login_page.html", ctx)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            return redirect(XXX)


class RegisterView(View):
    def get(self, request):
        return render(request, "register_page.html", {})
