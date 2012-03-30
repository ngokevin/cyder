from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from cyder.core.ctnr.models import Ctnr

class DevAuthenticationMiddleware(object):

    def process_request(self, request):

        # login as development user
        if request.user.is_anonymous():
            request.user = authenticate(username='development', password='development')
            if request.user:
                login(request, request.user)

            # set session ctnr on login to user's default ctnr
            default_ctnr = request.user.get_profile().default_ctnr
            if not default_ctnr:
                request.session['ctnr'] = Ctnr.objects.get(id=1)
            else:
                request.session['ctnr'] = Ctnr.objects.get(id=default_ctnr.id)
        else:
            # from cyder.cydns.domain.models import Domain
            # domain = Domain.objects.get(id=1)
            # print request.user.get_profile().has_perm(request, 'create', domain)
            return None
