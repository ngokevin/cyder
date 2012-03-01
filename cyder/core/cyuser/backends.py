from cyder.core.ctnr.models import Ctnr, Ctnr_User

class AuthorizationBackend(object):

    def has_perm(self, user_obj, perm, obj=None):

        # ctnr_user = Ctnr_User.objects.get(ctnr=request.session
