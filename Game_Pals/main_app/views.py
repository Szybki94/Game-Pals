# django modules
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import generic, View

# Python modules
from datetime import date, datetime, timedelta

# my modules
import calendar
from .forms import LoginForm, RegisterForm, UserUpdateForm1, UserUpdateForm2, UserAddEventForm, UserGameDeleteForm
from .models import Event, Game, UserGames, Profile
from .utils import Calendar


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


class MainView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return redirect("login")


class HomeView(generic.ListView):
    model = Event
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        context['games'] = self.request.user.games.all().order_by('name')

        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Previous and next month pass to context
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        # Instantiate our calendar class with today's year and date
        cal = Calendar(self.request.user, d.year, d.month)

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
            if not profile.avatar:
                profile.avatar = 'avatars/random_avatar.jpg'
            profile.personal_info = form.cleaned_data["personal_info"]
            profile.save()
            messages.success(request, "Step 3/3 completed")
            return redirect("home")
        else:
            messages.success(request, "Something went wrong, please try again")
            return render(request, "register_page_3.html", {"form": form})


class UserAddEventView(View):
    def get(self, request):
        ctx = {
            'form': UserAddEventForm,
            'user': request.user,
            'profile': request.user.profile,
            'games': request.user.games.all()
        }
        return render(request, 'User_add_event.html', ctx)


class UserAddGamesView(View):
    ctx = {"form": UserUpdateForm1}

    def get(self, request):
        return render(request, "add_games.html", self.ctx)

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
            return redirect("home")
        else:
            return render(request, "add_games.html", {"form": form})


class UserDeleteGameView(View):
    # Robię w taki sposób bo nie bardzo wiem jak utworzyć queryset pobierający UserGames id w DeleteView
    def get(self, request, game_id):
        context = {}
        user = request.user
        context['form'] = UserGameDeleteForm
        context['user'] = request.user
        context['profile'] = request.user.profile
        context['games'] = request.user.games.all().order_by('name')
        return render(request, "delete_games.html", context)

    def post(self, request, game_id):
        form = UserGameDeleteForm(request.POST)
        user_id = request.user.id
        game_id = game_id
        if form.is_valid():
            # Sposób poniżej otrzymam słownik, ale tylko z jedną pozycją spełniającą warunek User.id + Game.id
            # w taki sposób mogę wymusić na formularzu usunięcie odpowiedniej relacji w tabeli UserGames
            queryset = UserGames.objects.filter(Q(game_id=game_id) & Q(user_id=user_id))
            user_game_id = queryset[0].id
            UserGames.objects.filter(id=user_game_id).delete()
            return redirect('home')


class UserSearchView(View):

    def get(self, request):
        context = {}
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        context['games'] = self.request.user.games.all().order_by('name')
        return render(request, "user_search.html", context)

    def post(self, request):
        context = {}
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        context['games'] = self.request.user.games.all().order_by('name')
        query = self.request.POST.get('username')
        searched_users = User.objects.filter(username__contains=query)
        message = "There is no search results"
        context['users'] = searched_users
        context['message'] = message
        return render(request, "user_search.html", context)


# class UserSearchView(generic.ListView):
#     template_name = "user_search.html"
#     model = User
#
#     def get_queryset(self):
#         query = self.request.GET('username')
#         if query:
#             searched_users = User.objects.filter(username__contains=query)
#         else:
#             searched_users = User.objects.none()
#         return searched_users
