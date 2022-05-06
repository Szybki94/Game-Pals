# django modules
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import generic, View

# Python modules
from datetime import date, datetime, timedelta

# my modules
import calendar
from .forms import LoginForm, RegisterForm, UserUpdateForm1, UserUpdateForm2, UserAddEventForm, UserGameDeleteForm, \
    SendFriendInvitationForm, CreateGroupForm
from .models import Event, Game, UserGames, Profile, Invitation, Group, UserGroup
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

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "login_page.html", {'form': LoginForm})

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
            return render(request, "login_page.html", {})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")


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
        return render(request, 'User_add_event.html', {'form': UserAddEventForm})

    def post(self, request):
        user = request.user
        title = request.POST.get('name')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        # Queryset dla utworzenia Eventu (atomic, bo chcę żeby wszystko poleciało razem
        with transaction.atomic():
            new_event = Event.objects.create(name=title, description=description, start_time=start_time)
            # Połączenie eventu z użytkownikiem
            user.user_events.add(Event.objects.get(id=new_event.id))
        return redirect('home')


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
        return render(request, "user_search.html", context)

    def post(self, request):
        context = {}
        query = self.request.POST.get('username')
        searched_users = User.objects.filter(username__contains=query)
        message = "There is no search results"
        context['users'] = searched_users
        context['message'] = message
        return render(request, "user_search.html", context)


class EventDetailsView(generic.DetailView):
    template_name = "event_detail.html"

    # Nadpisanie funkcji zwracającej obiek, ponieważ nie chce w URL'u mieć <int: pk>, bo brzydko wygląda :P
    def get_object(self):
        id_url = self.kwargs.get("event_id")
        return get_object_or_404(Event, id=id_url)


class UserDetailsView(View):

    def get(self, request, user_id):
        context = {}
        user = request.user
        context['searched_user'] = User.objects.get(id=user_id)
        context['form'] = SendFriendInvitationForm
        return render(request, "user_detail.html", context)

    def post(self, request, user_id):
        form = SendFriendInvitationForm(request.POST)
        if form.is_valid():
            Invitation.objects.create(sender_id=request.user.id, receiver_id=user_id)
        return redirect("home")


class FriendRequestsView(View):
    def get(self, request):
        context = {}
        context['user_friend_requests'] = Invitation.objects.filter(
            Q(receiver_id=request.user.id) & Q(accepted__isnull=True))
        context['user_sent_requests'] = Invitation.objects.filter(
            Q(sender_id=request.user.id) & Q(accepted__isnull=True))
        return render(request, "friend_requests.html", context)

    def post(self, request):
        context = {}
        context['user_friend_requests'] = Invitation.objects.filter(
            Q(receiver_id=request.user.id) & Q(accepted__isnull=True))
        relationship = Invitation.objects.get(id=request.POST.get('request'))
        if request.POST.get('answer') == "Submit":
            relationship.accepted = 1
            relationship.save()
            return redirect('friend_requests')
        elif request.POST.get('answer') == "Decline" or "Cancel":
            relationship.delete()
            return redirect('friend_requests')


class GroupCreateView(generic.CreateView):
    template_name = "create_group.html"
    form_class = CreateGroupForm
    #  Do zmiany, chcę później przekierować na listę grup, w których jest gracz :)
    success_url = "../home"

    # Nadpisuję inicjację formularza Django z wypełnionym polem create_by
    def get_initial(self):
        self.initial.update({'created_by': self.request.user})
        return self.initial


@receiver(post_save, sender=Group)
def create_usergroup(sender, instance, created, **kwargs):
    # instance == Group w group stworzyłem FK do User'a, żeby przemycić jego PK do wypełnienia
    if created:
        UserGroup.objects.create(group=instance, user_id=instance.created_by.id, is_admin=1, is_extra_user=1)


class UserGroupsView(generic.ListView):
    model = UserGroup
    template_name = "groups_list.html"

    def get_queryset(self):
        queryset = super(UserGroupsView, self).get_queryset()
        queryset = queryset.filter(user_id=self.request.user.id)
        return queryset


# class GroupDetailView(View):
#     def get(self, request, group_id):
#         return HttpResponse('''Tu będzie widok szczegółów grupy wraz z jej kalendarzemi<br>
#                             i możliwością dodawania komentarzy<br>''')


class GroupDetailView(View):
    html = "group_detail.html"  # do zrobienia
    context = {}

    def get(self, request, group_id):
        self.context['group'] = Group.objects.get(id=group_id)
        self.context['group_members'] = UserGroup.objects.filter(group_id=group_id)
        return render(request, self.html, self.context)
