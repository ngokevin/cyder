import simplejson

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect

from cyder.core.ctnr.models import Ctnr, CtnrUser

class DevAuthenticationMiddleware(object):

    def process_request(self, request):

        # automatically 'log in' development user
        if request.user.is_anonymous():

            # manually log on user, must do it this way so django knows
            # user is properly authenticated and doesn't force log out
            user = authenticate(username='development', password='development')
            login(request, user)

            # set session ctnr on login to user's default ctnr
            default_ctnr = request.user.get_profile().default_ctnr
            if not default_ctnr:
                request.session['ctnr'] = Ctnr.objects.get(id=1)
            else:
                request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)

            # load session vars to load templates up with ctnr data
            request.session['level'] = CtnrUser.objects.get(user=request.user, ctnr=default_ctnr).level

            try:
                # get all of ctnrs for user to switch between
                global_ctnr = CtnrUser.objects.get(user=request.user, ctnr=1)
                if global_ctnr:
                    request.session['ctnrs'] = list(Ctnr.objects.all())

                    # set user as superuser if so
                    if global_ctnr.level == 2:
                        request.session['superuser'] = True

                # to set up the bootstrap typeahead ctnr search bar
                names = Ctnr.objects.all().values_list('name', flat=True)
                names = sorted([str(name) for name in names], key=str.lower)
                request.session['ctnr_names_json'] = simplejson.dumps(names)

            except CtnrUser.DoesNotExist:
                # get all of user's ctnrs for user to switch between
                ctnrs_user = CtnrUser.objects.filter(user=request.user)
                ctnrs = ctnrs_user.values_list('ctnr', flat=True)
                request.session['ctnrs'] = ctnrs

                # to set up the bootstrap typeahead ctnr search bar
                names = sorted([str(ctnr.name) for ctnr in ctnrs], key=str.lower)
                request.session['ctnr_names_json'] = simplejson.dumps(names)

        if request.path == '/logout/':
            request.session.flush()
            return redirect('/')

        return None
