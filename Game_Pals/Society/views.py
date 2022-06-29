from django.contrib.auth.admin import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView

# MODELS
from Home.models import Friendship, Profile, UserGames
from User.models import Event

# PYTHON MODULES
import calendar
from datetime import date, datetime, timedelta

# FORMS
from .forms import SendFriendInvitationForm


# MY UTILS
from .utils import FriendCalendar


# MIXINS
class FriendshipMixin(UserPassesTestMixin):
    def test_func(self, **kwargs):
        user = self.request.user
        user_profile = user.profile
        other_user = User.objects.get(id=self.kwargs.get('friend_id'))
        other_user_profile = other_user.profile

        if Friendship.objects.filter \
                    (sender=user_profile,
                     receiver=other_user_profile,
                     accepted=True).exists():
            return True
        elif Friendship.objects.filter \
                    (sender_id=other_user_profile,
                     receiver_id=user_profile,
                     accepted=True).exists():
            return True
        else:
            return False

    def handle_no_permission(self):
        return redirect('user:home-view')


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


# VIEWS
class UserSearchView(View):

    def get(self, request):
        context = {}
        return render(request, "00_main_looks/user_search.html", context)

    def post(self, request):
        context = {}
        query = self.request.POST.get('username')
        searched_users = User.objects.filter(username__contains=query)
        message = "There is no search results"
        context['users'] = searched_users
        context['message'] = message
        return render(request, "00_main_looks/user_search.html", context)


class UserDetailsView(View):

    def get(self, request, user_id):
        context = {}

        # Some variables for clean code
        user = request.user
        user_profile = user.profile
        other_user = User.objects.get(id=user_id)
        other_user_profile = other_user.profile

        # Code bellow responsible for getting info about searched user
        context['searched_user'] = User.objects.get(id=user_id)
        context['user_games'] = UserGames.objects.filter(user_id=user_id)

        # Code bellow is for checking invitations status for loading form in page
        context['form'] = SendFriendInvitationForm()
        context['friends_list'] = request.user.profile.friends.filter()

        # Check for invitation as sender
        try:
            context['user_sender'] = Friendship.objects.get(sender=user_profile, receiver=other_user_profile)
        except Friendship.DoesNotExist:
            context['sender'] = None

        # Check for invitation as receiver
        try:
            context['user_receiver'] = Friendship.objects.get(receiver=user_profile, sender=other_user_profile)
        except Friendship.DoesNotExist:
            context['user_receiver'] = None

        # Code below is redirecting user for Pal calendar if they have friendship relation
        if Friendship.objects.filter(
                            sender=user_profile,
                            receiver=other_user_profile,
                            accepted=True).exists() \
                or Friendship.objects.filter(
                            sender=other_user_profile,
                            receiver=user_profile,
                            accepted=True).exists():
            return redirect('society:friend_calendar', friend_id=user_id)
        return render(request, "00_main_looks/user_detail.html", context)

    def post(self, request, user_id):
        # Some variables for clean code
        user = request.user
        user_profile = user.profile
        other_user = User.objects.get(id=user_id)
        other_user_profile = other_user.profile

        form = SendFriendInvitationForm(request.POST)
        if form.is_valid():
            Friendship.objects.create(sender_id=user_profile.id, receiver_id=other_user_profile.id)
        return redirect("society:user_search")


class FriendRequestsView(View):
    def get(self, request):
        context = {}
        context['user_friend_requests'] = Friendship.objects.filter(
            Q(receiver_id=request.user.profile) & Q(accepted__isnull=True))
        context['user_sent_requests'] = Friendship.objects.filter(
            Q(sender_id=request.user.profile) & Q(accepted__isnull=True))
        return render(request, "00_main_looks/friend_requests.html", context)

    def post(self, request):
        context = {}
        context['user_friend_requests'] = Friendship.objects.filter(
            Q(receiver_id=request.user.id) & Q(accepted__isnull=True))
        relationship = Friendship.objects.get(id=request.POST.get('request'))
        if request.POST.get('answer') == "Submit":
            relationship.accepted = 1
            relationship.save()
            return redirect('society:friend_requests')
        elif request.POST.get('answer') == "Decline" or "Cancel":
            relationship.delete()
            return redirect('society:friend_requests')


class UserPalsView(ListView):
    model = Friendship
    template_name = '00_main_looks/friend_list.html'

    # Overwrite queryset method because is need to connect records where user is SENDER and RECEIVER
    def get_queryset(self):
        queryset = super(UserPalsView, self).get_queryset()
        queryset = Friendship.objects \
            .filter(sender=self.request.user.profile, accepted=True) \
            .union(Friendship.objects.filter(receiver=self.request.user.profile, accepted=True))
        return queryset


class DeleteFriendship(DeleteView):
    model = Friendship
    success_url = reverse_lazy('society:user_pals')


# Should add bellow FriendshipMixin,
class FriendCalendarView(FriendshipMixin, View):
    context = {}

    def get(self, request, friend_id):
        self.context['friend'] = User.objects.get(id=friend_id)
        # Code below responsible for Calendar
        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Previous and next month pass to context
        d = get_date(self.request.GET.get('month', None))
        self.context['prev_month'] = prev_month(d)
        self.context['next_month'] = next_month(d)

        # Instantiate our calendar class with today's year and date
        cal = FriendCalendar(User.objects.get(id=friend_id), d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        self.context['calendar'] = mark_safe(html_cal)

        return render(request, '00_main_looks/friend_calendar.html', self.context)


# Should add bellow FriendshipMixin,
class FriendEventDetailsView(FriendshipMixin, DetailView):
    template_name = "friend_event_detail.html"

    def get_object(self):
        event_id = self.kwargs.get("event_id")
        return get_object_or_404(Event, id=event_id)
