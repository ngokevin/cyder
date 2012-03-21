from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from cyder.cydns.domain.models import Domain
from cyder.settings import CYDNS_BASE_URL
from cyder.cydns.models import ObjectUrlMixin
from cyder.cydns.cydns import _validate_label, _validate_name
import pdb

class CommonRecord(models.Model, ObjectUrlMixin):
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
