from cyder.core.container.models import CTNR, CTNR_User

class ContainerBackend(object):

    def has_perm(self, user_obj, perm, obj=None):
