from django.core.exceptions import ObjectDoesNotExist


def user_processor(request):
    context = {}
    try:
        context['user'] = request.user
        context['profile'] = request.user.profile
        context['games'] = request.user.games.all().order_by('name')
    except (ObjectDoesNotExist, AttributeError):
        return {}
    return context
