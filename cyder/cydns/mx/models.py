from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import _check_TLD_condition
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cname.models import CNAME

from cyder.cydns.validation import  validate_ttl, validate_name, validate_mx_priority

class MX(CommonRecord):
    id              = models.AutoField(primary_key=True)
    # The mail server this record should point to.
    server          = models.CharField(max_length=100, validators=[validate_name])
    priority        = models.PositiveIntegerField(null=False, validators=[validate_mx_priority])
    ttl             = models.PositiveIntegerField(null=False, validators=[validate_ttl])

    def details(self):
        return  (
                    ('FQDN', self.fqdn),
                    ('Record Type', 'MX'),
                    ('Server', self.server),
                    ('Priority', self.priority),
                    ('TTL', self.ttl)
                )
    class Meta:
        db_table = 'mx'
        # label and domain in CommonRecord
        unique_together = ('domain', 'label', 'server', 'priority')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MX, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super(MX, self).clean(*args, **kwargs)
        super(MX, self).check_for_delegation()

        _check_TLD_condition(self)
        self._validate_no_cname()

    def __str__(self):
        return "%s %s %s %s %s %s" % (self.fqdn, self.ttl, 'IN', 'MX',\
                                        self.priority, self.server)
    def __repr__(self):
        return "<MX '%s'>" % (str(self))

    def _validate_no_cname(self):
        """MX records should not point to CNAMES."""
        # TODO, cite an RFC.
        if CNAME.objects.filter( fqdn = self.server ):
            raise ValidationError("MX records should not point to CNAMES.")
