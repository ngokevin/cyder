from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.validation import validate_label, validate_name
from cyder.cydns.models import ObjectUrlMixin


class BaseNameserver(models.Model, ObjectUrlMixin):
    id = models.AutoField(primary_key=True)
    server = models.CharField(max_length=255, validators=[validate_name])

    class Meta:
        abstract = True

    def clean(self):
        self._check_NS_TLD_condition()

    def _check_NS_TLD_condition(ns):
        domain = Domain.objects.filter(name=ns.server)
        if not domain:
            return
        else:
            raise ValidationError("You cannot create a NS record that is the"
                                  "name of a domain.")
