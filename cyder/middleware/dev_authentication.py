import simplejson

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

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
                    request.session['ctnrs'] = Ctnr.objects.all()

                    # set user as superuser if so
                    if global_ctnr.level == 2:
                        request.session['superuser'] = True

                # to set up the bootstrap typeahead ctnr search bar
                ctnrs = Ctnr.objects.all()
                ctnr_names = [ctnr.name for ctnr in ctnrs]
                request.session['ctnr_names_json'] = simplejson.dumps(ctnr_names)
            except CtnrUser.DoesNotExist:
                # get all of user's ctnrs for user to switch between
                ctnrs_user = CtnrUser.objects.filter(user=request.user)
                request.session['ctnrs'] = [ctnr_user.ctnr for ctnr_user in ctnrs_user]


                # to set up the bootstrap typeahead ctnr search bar
                ctnr_names = [ctnr_user.ctnr.name for ctnr_user in ctnrs_user]
                request.session['ctnr_names_json'] = simplejson.dumps(ctnr_names)

        return None
