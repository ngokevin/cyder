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

            # get all of user's ctnrs for user to switch between
            try:
                global_ctnr = CtnrUser.objects.get(user=request.user, ctnr=1)
                if global_ctnr:
                    request.session['ctnrs'] = Ctnr.objects.all()
            except CtnrUser.DoesNotExist:
                ctnrs_user = CtnrUser.objects.filter(user=request.user)
                request.session['ctnrs'] = [ctnr_user.ctnr for ctnr_user in ctnrs_user]

        return None
