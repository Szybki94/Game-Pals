from django.contrib.auth.admin import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.views import View
from django.views.generic import ListView


# MODELS
from Home.models import Friendship, Profile, UserGames

# PYTHON MODULES


# FORMS
from .forms import SendFriendInvitationForm


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

        # Poniższy fragment kodu przekieruje na kalendarz użytkownika, jeśli są znajomymi
        # if Invitation.objects.filter(sender_id=request.user.id, receiver_id=user_id, accepted=True).exists() \
        #         or Invitation.objects.filter(sender_id=user_id, receiver_id=request.user.id, accepted=True).exists():
        #     return redirect('friend-calendar', friend_id=user_id)
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