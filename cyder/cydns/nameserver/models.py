from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.validation import validate_label, validate_name
from cyder.cydns.models import ObjectUrlMixin
import pdb


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


class ReverseNameserver(BaseNameserver):
    """Name server for reverse domains.

    >>> ReverseNameserver(reverse_domain = reverse_domain, server = server)

    """
    reverse_domain = models.ForeignKey(ReverseDomain, null=False)

    class Meta:
        db_table = 'reverse_nameserver'
        unique_together = ('reverse_domain', 'server')

    def get_absolute_url(self):
        return "/cyder/cydns/reverse_nameserver/{0}/detail".format(self.pk)

    def details(self):
        details = (
                    ('Server', self.server),
                    ('Reverese Domain', self.reverse_domain.name),
                  )
        return tuple(details)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ReverseNameserver, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} {1} {2}".format(self.reverse_domain.name, 'NS',
                                    self.server)

    def __repr__(self):
        return "<Reverse '{0}'>".format(str(self))


class Nameserver(BaseNameserver):
    """Name server for forward domains::

    >>> Nameserver(domain = domain, server = server)

    """
    domain = models.ForeignKey(Domain, null=False)
    # "If the name server does lie within the domain it should have a
    # corresponding A record."
    glue = models.ForeignKey(AddressRecord, null=True, blank=True)

    class Meta:
        db_table = 'nameserver'
        unique_together = ('domain', 'server')

    def details(self):
        details = [
                    ('Server', self.server),
                    ('Domain', self.domain.name),
                  ]
        if self.glue:
            details.append(('Glue', self.glue))
        return tuple(details)

    def clean(self):
        super(Nameserver, self).clean()

        if not self._needs_glue():
            self.glue = None
        else:
            # Try to find any glue record. It will be the first elligible
            # A record found.
            glue_label = self.server.split('.')[0]  # foo.com -> foo
            glue = AddressRecord.objects.filter(label=glue_label,
                                                domain=self.domain)
            if not glue:
                raise ValidationError("NS needs glue record. Create a glue "
                                      "record for the server before creating "
                                      "the NS record.")
            else:
                self.glue = glue[0]

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Nameserver, self).save(*args, **kwargs)

    def __repr__(self):
        return "<Forward '{0}'>".format(str(self))

    def __str__(self):
        return "{0} {1} {2}".format(self.domain.name, 'NS', self.server)

    def _needs_glue(self):
        # Replace the domain portion of the server with "".
        # if domain == foo.com and server == ns1.foo.com.
        #       ns1.foo.com --> ns1
        try:
            possible_label = self.server.replace("." + self.domain.name, "")
        except ObjectDoesNotExist:
            return False

        if possible_label == self.server:
            return False
        try:
            validate_label(possible_label)
        except ValidationError:
            # It's not a valid label
            return False
        return True
