from django.contrib.auth.admin import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.views import View


# MODELS
from Home.models import Friendship, UserGames

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
        user = request.user
        context['searched_user'] = User.objects.get(id=user_id)
        context['user_games'] = UserGames.objects.filter(user_id=user_id)
        # context['friends_list'] = request.user.profile.friendship.filter()
        context['form'] = SendFriendInvitationForm()
        # Zamieszanie ze sprawdzaniem istniejącego invitation:
        try:
            context['user_friendship'] = Friendship.objects.get(sender_id=request.user.id, receiver_id=user_id)
        except Friendship.DoesNotExist:
            context['user_friendship'] = None
        try:
            context['receiver_friendship'] = Friendship.objects.get(sender_id=user_id, receiver_id=request.user.id)
        except Friendship.DoesNotExist:
            context['receiver_friendship'] = None
        context['user_friendships'] = Friendship.objects.filter(sender_id=request.user.id)
        context['receiver_friendships'] = Friendship.objects.filter(sender_id=user_id)

        # Poniższy fragment kodu przekieruje na kalendarz użytkownika, jeśli są znajomymi
        # if Invitation.objects.filter(sender_id=request.user.id, receiver_id=user_id, accepted=True).exists() \
        #         or Invitation.objects.filter(sender_id=user_id, receiver_id=request.user.id, accepted=True).exists():
        #     return redirect('friend-calendar', friend_id=user_id)
        return render(request, "00_main_looks/user_detail.html", context)

    def post(self, request, user_id):
        form = SendFriendInvitationForm(request.POST)
        if form.is_valid():
            Friendship.objects.create(sender_id=request.user.id, receiver_id=user_id)
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
