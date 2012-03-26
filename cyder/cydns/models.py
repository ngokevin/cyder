from cyder.settings import CYDNS_BASE_URL

class ObjectUrlMixin(object):
    """
    This is a mixin that adds important url methods to a model. This class uses the
    ``_meta.app_label`` instance variable of an object to calculate URLs. Because of this, you must
    use the app label of your class when declaring urls in your urls.py.
    """
    # TODO, does app_label cause name collision when models share an app (i.e. nameservers
    # and reverse nameservers? If true, we may need to use something other than app_label.

    def get_absolute_url(self):
        """Return the absolute url of an object."""
        return CYDNS_BASE_URL + "/%s/%s/detail" % (self._meta.app_label, self.pk)

    def get_edit_url(self):
        """Return the edit url of an object."""
        return CYDNS_BASE_URL + "/%s/%s/update" % (self._meta.app_label, self.pk)

    def get_delete_url(self):
        """Return the delete url of an object."""
        return CYDNS_BASE_URL + "/%s/%s/delete" % (self._meta.app_label, self.pk)
