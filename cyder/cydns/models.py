from cyder.settings import CYDNS_BASE_URL

class ObjectUrlMixin(object):
    """A mixin that adds important url methods to a model."""
    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/%s/%s/detail" % (self._meta.app_label, self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/%s/%s/update" % (self._meta.app_label, self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/%s/%s/delete" % (self._meta.app_label, self.pk)
