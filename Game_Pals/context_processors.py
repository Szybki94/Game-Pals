from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def user_processor(request):
    context = {}
    try:
        context['USER'] = request.user
        context['PROFILE'] = request.user.profile
        context['GAMES'] = request.user.games.all().order_by('name')
        # context['FRIENDS'] = request.user.profile.friends.all().order_by('username')
        # This part is responsible for Friends mechanism
        # friend_requests = Invitation.objects.filter(Q(receiver_id=request.user.id) & Q(accepted__isnull=True)).count()
        # if friend_requests == 0:
        #     context['friend_requests'] = ""
        # else:
        #     context['friend_requests'] = friend_requests
    except (ObjectDoesNotExist, AttributeError):
        return {}
    return context
