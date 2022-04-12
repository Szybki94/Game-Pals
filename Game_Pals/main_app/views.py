# django moduls
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import (
    login_required,
)
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import generic, View

# Python moduls
from datetime import date, datetime

# my moduls
from .forms import LoginForm, RegisterForm, UserUpdateForm1, UserUpdateForm2
from .models import Event, Game, Profile
from .utils import Calendar


class MainView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return redirect("login")


# class HomeView(View):
#     ctx = {}
#
#     def get(self, request):
#         user = request.user
#         profile = user.profile
#         games = user.games.all()
#         self.ctx = {
#             "profile": profile,
#             "games": games,
#         }
#
#         return render(request, "home.html", self.ctx)

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


class HomeView(generic.ListView):
    model = Event
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        context['games'] = self.request.user.games.all()

        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        return context


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
            messages.success(request, "Step 1/3 completed")
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)  # Odrazu loguje użytkownika
            return redirect("/update-user-1/")
        else:
            messages.error(request, form.errors)
            return render(request, "register_page.html", {"form": form})


# Funkcja tworząca i łącząca nowy profil do nowo zarejestrowanego użytkownika
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class UserUpdateView1(View):
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
            return redirect("user-update-2")
        else:
            messages.success(request, form.errors)
            return render(request, "register_page_2.html", {"form": form})


class UserUpdateView2(View):

    def get(self, request):
        ctx = {"form": UserUpdateForm2}
        return render(request, "register_page_3.html", ctx)

    def post(self, request):
        form = UserUpdateForm2(request.POST, request.FILES)
        user = request.user
        ctx = {"form": UserUpdateForm2}
        if form.is_valid():
            profile = user.profile
            profile.avatar = form.cleaned_data["avatar"]
            profile.personal_info = form.cleaned_data["personal_info"]
            profile.save()
            messages.success(request, "Step 3/3 completed")
            return redirect("home")
        else:
            messages.success(request, "Something went wrong, please try again")
            return render(request, "register_page_3.html", {"form": form})

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
