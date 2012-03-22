from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from cyder.cydns.domain.models import Domain
from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.models import ObjectUrlMixin
from cyder.cydns.cydns import _validate_label, _validate_name
import pdb

class CommonRecord(models.Model, ObjectUrlMixin):
    """
    This class provides common functionality that many DNS record classes share.  This includes a
    foreign key to the ``domain`` table and a ``label`` CharField.  This class also inherits from
    the ``ObjectUrlMixin`` class to provide the ``get_absolute_url``, ``get_edit_url``, and
    ``get_delete_url`` functions.

    This class does validation on the ``label`` field. Call ``clean_all`` to trigger the validation
    functions. Failure to validate will raise a ``ValidationError``.

    If you plan on using the ``unique_together`` constraint on a Model that inherits from
    ``CommonRecord``, you must include ``domain`` and ``label`` explicitly if you need them to.
    ``CommonRecord`` will not enforce uniqueness for you.
    """

    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100, blank=True,\
                        null=True, validators=[_validate_label])

    class Meta:
        abstract = True

    def clean( self ):
        _validate_name( self.fqdn() ) # This may causes duplicate errors.

    def fqdn(self):
        try:
            if self.label == '':
                fqdn = self.domain.name
            else:
                fqdn = "%s.%s" % (self.label, self.domain.name)
        except ObjectDoesNotExist:
            return
        return fqdn
