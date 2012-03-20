from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import _check_TLD_condition
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import  _validate_ttl, _validate_name

def _validate_mx_priority(priority):
    if priority > 65535 or priority < 0:
        raise ValidationError("Error: MX priority must be within the 0 to 65535\
            range. See RFC 1035")

class MX(CommonRecord):
    id              = models.AutoField(primary_key=True)
    # The mail server this record should point to.
    server          = models.CharField(max_length=100, validators=[_validate_name])
    priority        = models.PositiveIntegerField(null=False, validators=[_validate_mx_priority])
    ttl             = models.PositiveIntegerField(null=False, validators=[_validate_ttl])

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
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
        _check_TLD_condition(self)

    def __str__(self):
        return "%s %s %s %s %s %s" % (self.fqdn(), self.ttl, 'IN', 'MX',\
                                        self.priority, self.server)
    def __repr__(self):
        return "<MX '%s'>" % (str(self))

