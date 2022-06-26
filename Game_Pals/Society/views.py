from django.contrib.auth.admin import User
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.views import View


# MODELS


# PYTHON MODULES


# FORMS


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
        context['friends_list'] = request.user.profile.friends.filter()
        context['form'] = SendFriendInvitationForm()
        # Zamieszanie ze sprawdzaniem istniejącego invitation:
        try:
            context['user_invitation'] = Invitation.objects.get(sender_id=request.user.id, receiver_id=user_id)
        except Invitation.DoesNotExist:
            context['user_invitation'] = None
        try:
            context['receiver_invitation'] = Invitation.objects.get(sender_id=user_id, receiver_id=request.user.id)
        except Invitation.DoesNotExist:
            context['receiver_invitation'] = None
        context['user_invitations'] = Invitation.objects.filter(sender_id=request.user.id)
        context['receiver_invitations'] = Invitation.objects.filter(sender_id=user_id)

        # Poniższy fragment kodu przekieruje na kalendarz użytkownika, jeśli są znajomymi
        # if Invitation.objects.filter(sender_id=request.user.id, receiver_id=user_id, accepted=True).exists() \
        #         or Invitation.objects.filter(sender_id=user_id, receiver_id=request.user.id, accepted=True).exists():
        #     return redirect('friend-calendar', friend_id=user_id)
        # return render(request, "user_detail.html", context)

    def post(self, request, user_id):
        form = SendFriendInvitationForm(request.POST)
        if form.is_valid():
            Invitation.objects.create(sender_id=request.user.id, receiver_id=user_id)
        return redirect("user_search")