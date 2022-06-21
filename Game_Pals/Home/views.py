from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, HttpResponse

from django.views import View


# Python modules


# my modules
from .forms import LoginForm, RegisterForm, UserUpdateForm1, UserUpdateForm2
from .models import Game, Profile


# ALL VIEWS BELOW

class MainView(View):
    # This view checks that user is logged or not. \
    # Then redirect him to proper page login/register

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("user:home-view")
        else:
            return redirect("home:login")


class LoginView(View):
    # Allow user to login

    ctx = {"form": LoginForm}

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:home")
        return render(request, "login_page.html", self.ctx)

    def post(self, request):
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You logged in")
            return redirect("user:home-view")
        else:
            messages.error(request, form.errors)
            return render(request, "login_page.html", {})


class RegisterView(View):
    # Allow new user to register

    ctx = {"form": RegisterForm}

    def get(self, request):
        return render(request, "register_page.html", self.ctx)

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)  # User log in instant
            return redirect("home:user-update-1")
        else:
            messages.error(request, form.errors)
            return render(request, "register_page.html", {"form": form})


# Function creating and connecting new profile to newly registered user
# It is an inseparable part of RegisterView (for code readability should be always bellow)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class UserUpdateView1(LoginRequiredMixin, View):
    ctx = {"form": UserUpdateForm1}

    def get(self, request):
        return render(request, "register_page_2.html", self.ctx)

    def post(self, request):
        form = UserUpdateForm1(request.POST)
        ctx = {'form': form}
        if form.is_valid():
            messages.success(request, "Step 2/3 completed")
            ctx['cleaned_data'] = form.cleaned_data
            games_id = [int(game) for game in ctx['cleaned_data']['games']]
            user = request.user
            for game_id in games_id:
                game = Game.objects.get(id=game_id)
                user.games.add(game)
            return redirect("home:user-update-2")
        else:
            messages.success(request, form.errors)
            return render(request, "register_page_2.html", {"form": form})


class UserUpdateView2(LoginRequiredMixin, View):
    ctx = {"form": UserUpdateForm2}

    def get(self, request):
        return render(request, "register_page_3.html", self.ctx)

    def post(self, request):
        form = UserUpdateForm2(request.POST, request.FILES)
        user = request.user
        ctx = {"form": UserUpdateForm2}
        if form.is_valid():
            profile = user.profile
            profile.avatar = form.cleaned_data["avatar"]
            if not profile.avatar:
                profile.avatar = 'avatars/random_avatar.jpg'
            profile.personal_info = form.cleaned_data["personal_info"]
            profile.save()
            messages.success(request, "Step 3/3 completed")
            return redirect("user:home-view")
        else:
            messages.success(request, "Something went wrong, please try again")
            return render(request, "register_page_3.html", {"form": form})


class LogoutView(LoginRequiredMixin, View):
    # Allow user to logout
    def get(self, request):
        logout(request)
        return redirect("home:home")
