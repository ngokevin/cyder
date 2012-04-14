from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def become_user(request, username=None):
    """
    Become another user with their permissions, be able to change back
    """
    referer = request.META.get('HTTP_REFERER', '/')

    try:
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
    except User.DoesNotExist:
        redirect(referer)

    redirect(referer)
