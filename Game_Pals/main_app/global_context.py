from .models import Profile, Game
from django.contrib.auth.models import User


def global_vars(request):
    return {
        'USER': request.user,
        'PROFILE': request.user.profile,
        'GAME': request.user.games.all(),
    }
