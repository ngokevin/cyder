from cyder.settings import CYDNS_BASE_URL

class ObjectUrlMixin(object):
    """
    This is a mixin that adds important url methods to a model. This class uses the
    ``_meta.app_label`` instance variable of an object to calculate URLs. Because of this, you must
    use the app label of your class when declaring urls in your urls.py.
    """
    # TODO. using app_label breaks shit. Go through all the models and assign a better field.
    # Something like "url handle".
    # TODO2. Using db_table for now. It looks weird, but it works.
    def get_absolute_url(self):
        """Return the absolute url of an object."""
        return CYDNS_BASE_URL + "/%s/%s/detail" % (self._meta.db_table, self.pk)

    def get_edit_url(self):
        """Return the edit url of an object."""
        return CYDNS_BASE_URL + "/%s/%s/update" % (self._meta.db_table, self.pk)

    def get_delete_url(self):
        """Return the delete url of an object."""
        return CYDNS_BASE_URL + "/%s/%s/delete" % (self._meta.db_table, self.pk)
