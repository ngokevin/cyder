from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain
from cyder.cydns.reverse_domain.models import ReverseDomain
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cydns import _validate_label, _validate_name
from cyder.cydns.models import ObjectUrlMixin
import pdb

class BaseNameserver(models.Model, ObjectUrlMixin):
    id              = models.AutoField(primary_key=True)
    server          = models.CharField(max_length=255, validators=[_validate_name])

    class Meta:
        abstract = True

    def clean(self):
        self._check_NS_TLD_condition()

    def _check_NS_TLD_condition(ns):
        domain = Domain.objects.filter(name = ns.server)
        if not domain:
            return
        else:
            raise ValidationError("You cannot create a NS record that is the name of a domain.")

class ReverseNameserver(BaseNameserver):
    """Name server for reverse domains."""
    reverse_domain          = models.ForeignKey(ReverseDomain, null=False)

    class Meta:
        db_table = 'reverse_nameserver'
        unique_together = ('reverse_domain', 'server')

    def details(self):
        details =  (
                    ('Reverese Domain', self.reverse_domain.name),
                    ('Server', self.server),
                   )
        return tuple(details)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ReverseNameserver, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s" % (self.reverse_domain.name, 'NS', self.server)

    def __repr__(self):
        return "<Reverse '%s'>" % (str(self))

class Nameserver(BaseNameserver):
    """ Name server for forward domains. """
    domain          = models.ForeignKey(Domain, null=False)
    # "If the name server does lie within the domain it should have a corresponding A record."
    glue            = models.ForeignKey(AddressRecord, null=True, blank=True)

    class Meta:
        db_table = 'nameserver'
        unique_together = ('domain', 'server')

    def details(self):
        details=[
                    ('Server', self.server),
                    ('Domain', self.domain.name),
                ]
        if self.glue: details.append(('Glue', self.glue))
        return tuple(details)


    def clean(self):
        super(Nameserver, self).clean()

        needs_glue = self._needs_glue()
        if self.glue and self.glue.fqdn() != self.server:
            if not needs_glue:
                raise ValidationError("Error: %s does not need a glue record." % (str(self)))
            else:
                raise ValidationError("Error: %s needs a correct glue record." % (str(self)))
        if not self.glue and needs_glue:
            raise ValidationError("Error: %s is in the %s domain. It needs a glue record." %\
                    (self.server, self.domain.name))


    def save(self, *args, **kwargs):
        self.full_clean()
        super(Nameserver, self).save(*args, **kwargs)


    def __repr__(self):
        return "<Forward '%s'>" % (str(self))

    def __str__(self):
        return "%s %s %s" % (self.domain.name, 'NS', self.server)

    def _needs_glue(self):
        # Replace the domain portion of the server with "".
        # if domain == foo.com and server == ns1.foo.com.
        #       ns1.foo.com --> ns1
        possible_label = self.server.replace("."+self.domain.name, "")
        try:
            _validate_label(possible_label)
        except ValidationError:
            # It's not a valid label
            return False
        return True

# TODO, re-write the view to not need this.
# Let's just have the ns record try to find a glue record for it's self. If it can't find one
# It can then throw an exception. This will remore the need to call this function in a view.
def _needs_glue(ns):
    # Replace the domain portion of the server with "".
    # if domain == foo.com and server == ns1.foo.com.
    #       ns1.foo.com --> ns1
    possible_label = ns.server.replace("."+ns.domain.name, "")
    try:
        _validate_label(possible_label)
    except ValidationError:
        # It's not a valid label
        return False
    return True

