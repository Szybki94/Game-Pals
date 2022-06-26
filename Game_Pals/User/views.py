from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView

# MODELS
from Home.models import Game, UserGames
from .models import Event

# PYTHON MODULES
import calendar
from datetime import date, datetime, timedelta

# FORMS
from .forms import EventDeleteForm, UserAddEventForm, UserGameDeleteForm
from Home.forms import UserUpdateForm1

# MY UTILS
from .utils import Calendar


# CALENDAR FUNCTIONS
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


# ALL VIEWS BELLOW
class HomeView(ListView):
    model = Event
    template_name = '00_main_looks/user-home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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


class UserAddEventView(View):
    def get(self, request):
        return render(request, '00_main_looks/User_add_event.html', {'form': UserAddEventForm})

    def post(self, request):
        user = request.user
        title = request.POST.get('name')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        # Atomic for safety connection event to user (they CAN NOT be separately)
        with transaction.atomic():
            new_event = Event.objects.create(name=title, description=description, start_time=start_time)
            # Connecting event with user
            user.user_events.add(Event.objects.get(id=new_event.id))
        return redirect('user:home-view')


class EventDetailsView(DetailView):
    template_name = "00_main_looks/event_detail.html"

    def get_object(self):
        id_url = self.kwargs.get("event_id")
        return get_object_or_404(Event, id=id_url)


class EventDeleteView(View):

    def get(self, request, event_id):
        ctx = {'form': EventDeleteForm,
               'event': Event.objects.get(id=event_id)}
        return render(request, "00_main_looks/event_delete_confirm.html", ctx)

    def post(self, request, event_id):
        form = EventDeleteForm(request.POST)
        if form.is_valid():
            Event.objects.get(id=event_id).delete()
        return redirect("user:home-view")


# Pace for user -> edit profile pic and personal info

# ---------------------------------------------------


class UserAddGamesView(View):
    ctx = {"form": UserUpdateForm1}

    def get(self, request):
        return render(request, "00_main_looks/add_games.html", self.ctx)

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
            return redirect("user:home-view")
        else:
            return render(request, "00_main_looks/add_games.html", {"form": form})


class UserDeleteGameView(View):
    def get(self, request, game_id):
        context = {}
        user = request.user
        context['form'] = UserGameDeleteForm
        return render(request, "00_main_looks/delete_games.html", context)

    def post(self, request, game_id):
        form = UserGameDeleteForm(request.POST)
        user_id = request.user.id
        game_id = game_id
        if form.is_valid():
            queryset = UserGames.objects.filter(Q(game_id=game_id) & Q(user_id=user_id))
            user_game_id = queryset[0].id
            UserGames.objects.filter(id=user_game_id).delete()
            return redirect('user:home-view')
