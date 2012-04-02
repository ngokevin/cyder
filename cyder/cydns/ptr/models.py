from django.db import models
from django.core.exceptions import ValidationError

from cyder.cydns.domain.models import Domain, _name_to_domain
from cyder.cydns.ip.models import Ip
from cyder.cydns.validation import validate_name
from cyder.cydns.models import ObjectUrlMixin

class PTR( Ip, ObjectUrlMixin ):
    """A PTR is used to map an IP to a domain name."""
    id              = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=255, validators=[validate_name])
    domain          = models.ForeignKey(Domain, null=True, blank=True)

    def details(self):
        return  (
                    ('Ip', str(self.ip_str)),
                    ('Record Type', 'PTR'),
                    ('Name', self.name),
                )
    class Meta:
        db_table = 'ptr'
        unique_together = ('ip_str', 'ip_type', 'name')

    def save(self, *args, **kwargs):
        if kwargs.has_key('update_reverse_domain'):
            urd = kwargs.pop('update_reverse_domain')
            self.clean_ip( update_reverse_domain = urd )
        else:
            self.clean_ip()
        self.full_clean()
        super(PTR, self).save(*args, **kwargs)

    def clean(self):
        self.domain = _name_to_domain(self.name)

    def __str__(self):
        return "%s %s %s" % (str(self.ip_str), 'PTR', self.name)

    def __repr__(self):
        return "<%s>" % (str(self))
