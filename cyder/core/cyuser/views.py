from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect

import simplejson

from cyder.core.ctnr.models import Ctnr, CtnrUser
from cyder.core.cyuser.models import UserProfile


def login_session(request, username):
    """
    Logs in a user and sets up the session.
    """
    # authenticate / login
    try:
        user = User.objects.get(username=username)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
    except User.DoesNotExist:
        messages.error(request, "User %s does not exist" % (username))
        return request

    # create user profile if needed
    try:
        request.user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
        profile.save()

    # assign user to default ctnr if needed
    try:
        CtnrUser.objects.get(user=request.user)
    except CtnrUser.DoesNotExist:
        new_default_ctnr = Ctnr.objects.get(id=2)
        CtnrUser(user=request.user, ctnr=new_default_ctnr, level=0).save()

    # set session ctnr
    default_ctnr = request.user.get_profile().default_ctnr
    if default_ctnr:
        request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)
    else:
        request.session['ctnr'] = Ctnr.objects.get(id=2)

    # set session ctnr level
    request.session['level'] = CtnrUser.objects.get(user=request.user, ctnr=default_ctnr).level

    try:
        # set ctnr list (to switch between)
        global_ctnr = CtnrUser.objects.get(user=request.user, ctnr=1)
        if global_ctnr:
            request.session['ctnrs'] = list(Ctnr.objects.all())

        # set ctnr json (for ctnr search bar)
        names = Ctnr.objects.all().values_list('name', flat=True)
        names = sorted([str(name) for name in names], key=str.lower)
        request.session['ctnr_names_json'] = simplejson.dumps(names)

    except CtnrUser.DoesNotExist:
        # set ctnr list (to switch between)
        ctnrs_user = CtnrUser.objects.filter(user=request.user)
        ctnrs = [Ctnr.objects.get(id=ctnr_pk) for ctnr_pk in  ctnrs_user.values_list('ctnr', flat=True)]
        request.session['ctnrs'] = ctnrs

        # set ctnr json (for ctnr search bar)
        names = sorted([str(ctnr.name) for ctnr in ctnrs], key=str.lower)
        request.session['ctnr_names_json'] = simplejson.dumps(names)

    return request


def become_user(request, username=None):
    """
    Become another user with their permissions, be able to change back
    """
    referer = request.META.get('HTTP_REFERER', '/')

    request = login_session(request, username)

    return redirect(referer)
