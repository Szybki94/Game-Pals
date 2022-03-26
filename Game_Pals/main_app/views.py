from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
)
from .forms import LoginForm, RegisterForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


# Create your views here.
class TEST(View):
    def get(self, request):
        return render(request, "test.html", {})


class MainView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return redirect("login")


class HomeView(View):
    def get(self, request):
        return render(request, "test.html", {})


class LoginView(View):
    ctx = {"form": LoginForm}

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "login_page.html", self.ctx)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You logged in")
            return redirect("home")
        else:
            messages.error(request, "Something went wrong, please try again")
            return render(request, "login", self.ctx)


class RegisterView(View):
    ctx = {"form": RegisterForm}

    def get(self, request):
        return render(request, "register_page.html", self.ctx)

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            # form.save()
            messages.success(request, "Registration completed")
            return redirect("home")
        else:
            messages.success(request, "Something went wrong, please try again")
            return render(request, "register_page.html", {"form": form})
