from django.shortcuts import render, redirect
from django.views import View
from .models import Game
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import (
    login_required,
)
from .forms import LoginForm, RegisterForm, UserUpdateForm1
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
            form.save()
            messages.success(request, "Registration completed")
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)  # Odrazu loguje użytkownika
            return redirect("/update-user-1/")
        else:
            messages.success(request, "Something went wrong, please try again")
            return render(request, "register_page.html", {"form": form})


class UserUpdateView1(View):
    ctx = {"form": UserUpdateForm1}

    def get(self, request):
        return render(request, "register_page_2.html", self.ctx)

    def post(self, request):
        form = UserUpdateForm1(request.POST)
        ctx = {'form': form}
        if form.is_valid():
            ctx['cleaned_data'] = form.cleaned_data
            games_id = [int(game) for game in ctx['cleaned_data']['games']]
            user = request.user
            for game_id in games_id:
                game = Game.objects.get(id=game_id)
                user.games.add(game)
            user_games = user.games.all()
            return HttpResponse(f"{user_games}")



class UserUpdateView2(View):
    ctx = {"form": ""}

    def get(self, request):
        user = request.user
        return HttpResponse(f"Witaj użytkowniku {user.username}")