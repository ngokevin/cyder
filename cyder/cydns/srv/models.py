from django.db import models
from django.core.exceptions import ValidationError
import cyder
from cyder.cydns.domain.models import Domain
from cyder.cydns.models import CydnsRecord
from cyder.cydns.validation import validate_name
from cyder.cydns.mixins import ObjectUrlMixin

from cyder.cydns.validation import validate_srv_label, validate_srv_port
from cyder.cydns.validation import validate_srv_priority, validate_srv_weight
from cyder.cydns.validation import validate_srv_name


# Rhetorical Question: Why is SRV not a common record?  SRV records have
# a '_' in their label. Most domain names do not allow this.  Cydns
# record has a validator that would raise an exception when validating
# it's label.  TODO, verify this.
class SRV(models.Model, ObjectUrlMixin):
    """
    >>> SRV(domain=domain, label=label, target=target, port=port,
    ... priority=priority, weight=weight)
    """
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100, blank=True, null=True,
                             validators=[validate_srv_label])

    domain = models.ForeignKey(Domain, null=False)
    fqdn = models.CharField(max_length=255, blank=True, null=True,
                            validators=[validate_srv_name])
    # fqdn = label + domain.name <--- see set_fqdn

    target = models.CharField(max_length=100,
                              validators=[validate_name])

    port = models.PositiveIntegerField(null=False,
                                       validators=[validate_srv_port])

    priority = models.PositiveIntegerField(null=False,
                                           validators=[validate_srv_priority])

    weight = models.PositiveIntegerField(null=False,
                                         validators=[validate_srv_weight])

    def details(self):
        return  (
                    ('FQDN', self.fqdn),
                    ('Record Type', 'SRV'),
                    ('Targer', self.target),
                    ('Port', self.port),
                    ('Priority', self.priority),
                    ('Weight', self.weight),
                )

    class Meta:
        db_table = 'srv'
        unique_together = ('label', 'domain', 'target', 'port',
                           'priority', 'weight')

    def delete(self, *args, **kwargs):
        super(SRV, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        self.domain.dirty = True
        self.domain.clean()
        super(SRV, self).save(*args, **kwargs)

    def clean(self):
        self.set_fqdn()
        self.check_for_cname()
        self.check_for_delegation()

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5} {6}".format(self.fqdn, 'IN', 'SRV',
                                                    self.priority, self.weight,
                                                    self.port, self.target)

    def __repr__(self):
        return "<{0}>".format(str(self))

    def set_fqdn(self):
        try:
            self.fqdn = "{0}.{1}".format(self.label, self.domain.name)
        except ObjectDoesNotExist:
            return

    def check_for_delegation(self):
        """If an object's domain is delegated it should not be able to
        be changed.  Delegated domains cannot have objects created in
        them.
        """
        if not self.domain.delegated:
            return
        if not self.pk:  # We don't exist yet.
            raise ValidationError("No objects can be created in the {0}"
                                   "domain. It is delegated.".
                                   format(self.domain.name))

    def check_for_cname(self):
        """"If a CNAME RR is preent at a node, no other data should be
        present; this ensures    that the data for a canonical name and
        its aliases cannot be different."

        -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

        Call this function in models that can't overlap with an existing
        CNAME.
        """
        CNAME = cyder.cydns.cname.models.CNAME
        if CNAME.objects.filter(fqdn=self.fqdn).exists():
            raise ValidationError("A CNAME with this name already exists.")
