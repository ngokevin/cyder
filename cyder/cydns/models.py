from cyder.settings import CYDNS_BASE_URL

class ObjectUrlMixin(object):
    """A mixin that adds important url methods to a model."""
    # TODO. using app_label breaks shit. Go through all the models and assign a better field.
    # Something like "url handle".
    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/%s/%s/detail" % (self._meta.app_label, self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/%s/%s/update" % (self._meta.app_label, self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/%s/%s/delete" % (self._meta.app_label, self.pk)
