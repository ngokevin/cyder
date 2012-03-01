from cyder.core.container.models import Container, Container_User

class AuthorizationBackend(object):

    def has_perm(self, user_obj, perm, obj=None):
