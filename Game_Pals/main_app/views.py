from django.shortcuts import render, redirect
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views import View
from .models import Game, Profile
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import (
    login_required,
)
from .forms import LoginForm, RegisterForm, UserUpdateForm1, UserUpdateForm2
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


# Funkcja tworząca i łącząca nowy profil do nowego użytkownika
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


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
    ctx = {}

    def get(self, request):
        profile_id = request.user.profile.id
        self.ctx['profile_id'] = profile_id
        return render(request, "test.html", self.ctx)


class LoginView(View):
    ctx = {"form": LoginForm}

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "login_page.html", self.ctx)

    def post(self, request):
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You logged in")
            return redirect("home")
        else:
            messages.error(request, form.errors)
            return render(request, "login_page.html", self.ctx)


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
            messages.error(request, form.errors)
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
            return redirect("user-update-2")
        else:
            messages.success(request, "Something went wrong, please try again")
            return render(request, "register_page_2.html", {"form": form})


class UserUpdateView2(View):

    def get(self, request):
        ctx = {"form": UserUpdateForm2}
        return render(request, "register_page_3.html", ctx)

    # def post(self, request):

        # form = UserUpdateForm2(request.POST)
        # ctx = {"form": form}
        # if form.is_valid():
        #     user = request.user
        #     user.profile.avatar = form.cleaned_data['avatar']
        #     user.profile.personal_info = form.cleaned_data['personal_info']
        #     user.update()
        #     return redirect("home")
        # else:
        #     messages.success(request, "Something went wrong, please try again")
        #     return render(request, "register_page_3.html", ctx)
