from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import _validate_name

class CNAME(CommonRecord):
    """
    CNAMES can't point to an MX record.
    """
    # TODO cite an RFC
    id              = models.AutoField(primary_key=True)
    data            = models.CharField(max_length=100, validators=[_validate_name])
    data_domain     = models.ForeignKey(Domain, null=True, related_name = 'data_domains', blank=True)

    def details(self):
        return  (
                    ('FQDN', self.fqdn),
                    ('Record Type', 'CNAME'),
                    ('Data', self.data),
               )

    class Meta:
        db_table = 'cname'
        unique_together = ('domain', 'label', 'data')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(CNAME, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super(CNAME, self).clean(*args, **kwargs)
        """The RFC for DNS requires that a CName never be at the same level as an SOA, A, or MX
        record. Bind enforces this restriction. When creating a Cname, the UI needs to make sure
        that there are no records of those types that will clash. Likewise, when creating an SOA, A
        or MX, the UI needs to verify that there are no MX records at that level. """
        # TODO ^
        self._check_SOA_condition()
        self.data_domain = _name_to_domain(self.data)
        self._validate_no_mx()

    def __str__(self):
        return "%s CNAME %s" % (self.fqdn, self.data)

    def _check_SOA_condition(self):
        domain = Domain.objects.filter(name = self.fqdn)
        if not domain:
            return
        # We need to check if the domain is the root domain in a zone.
        # The domain will have an soa, but the master domain will have no soa (or a different one)

        if domain[0].soa and domain[0].soa != domain[0].master_domain.soa:
            raise ValidationError("You cannot create a CNAME that points to a domain at the\
                                            root of a zone.")
        return

    def _validate_no_mx(self):
        """MX records should not point to CNAMES."""
        # TODO, cite an RFC.
        from cyder.cydns.mx.models import MX
        if MX.objects.filter(server = self.fqdn):
            raise ValidationError("MX records should not point to CNAMES.")
