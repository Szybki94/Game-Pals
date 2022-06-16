from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from main_app.models import Invitation, Group, Comment, UserGroup


def user_processor(request):
    context = {}
    try:
        context['user'] = request.user
        context['profile'] = request.user.profile
        context['games'] = request.user.games.all().order_by('name')
        context['friends'] = request.user.profile.friends.all().order_by('username')
        friend_requests = Invitation.objects.filter(Q(receiver_id=request.user.id) & Q(accepted__isnull=True)).count()
        if friend_requests == 0:
            context['friend_requests'] = ""
        else:
            context['friend_requests'] = friend_requests
    except (ObjectDoesNotExist, AttributeError):
        return {}
    return context
