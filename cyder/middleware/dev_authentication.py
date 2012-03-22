from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr

import pdb

class DevAuthenticationMiddleware(object):

    def process_request(self, request):

        # login as development user
        if request.user.is_anonymous():
            request.user = authenticate(username='development', password='development')
            if request.user:
                login(request, request.user)
            else:
                # manually create development user if not created already
                request.user = User()
                request.user.username = 'development'
                request.user.first_name = 'development'
                request.user.last_name = 'development'
                request.user.email = 'development@foo.bar.com'
                request.user.set_password('development')
                request.user.save()

            # set session ctnr on login to user's default ctnr
            default_ctnr = request.user.get_profile().default_ctnr
            if not default_ctnr:
                request.session['ctnr'] = Ctnr.objects.get(id=0)
            else:
                request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)
        else:
            print request.user.get_profile().has_perm(request, "LOL", None)
            return None
