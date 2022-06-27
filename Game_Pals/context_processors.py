from django.contrib.auth.admin import User
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


# MODELS
from Home.models import Friendship, Profile


def user_processor(request):
    context = {}
    try:
        context['USER'] = request.user
        context['PROFILE'] = request.user.profile
        context['GAMES'] = request.user.games.all().order_by('name')
        # Z linikją poniżej jest coś nie tak!!!
        context['FRIENDS'] = request.user.profile.friendship.all().order_by('user__username')
        # This part is responsible for Friends mechanism
        friend_requests = Friendship.objects.filter(Q(receiver_id=request.user.profile) & Q(accepted__isnull=True)).count()
        if friend_requests == 0:
            context['FRIEND_REQUESTS'] = ""
        else:
            context['FRIEND_REQUESTS'] = friend_requests
    except (ObjectDoesNotExist, AttributeError):
        return {}
    return context
