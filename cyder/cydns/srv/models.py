from django.db import models
from django.core.exceptions import ValidationError
from cyder.cydns.domain.models import Domain
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import _validate_name
from cyder.cydns.cydns import _validate_label
from cyder.cydns.models import ObjectUrlMixin

from cyder.cydns.srv.validators import _validate_srv_label, _validate_srv_port
from cyder.cydns.srv.validators import _validate_srv_priority, _validate_srv_weight
from cyder.cydns.srv.validators import _validate_srv_name

# Rhetorical Question: Why is SRV not a common record?
# SRV records have a '_' in their label. Most domain names do not allow this.
# Common record has a validator that would raise an exception when validating it's label.
# TODO, verify this.
class SRV(models.Model, ObjectUrlMixin):
    domain          = models.ForeignKey(Domain, null=False)
    label           = models.CharField(max_length=100, blank=True, null=True,\
                        validators=[_validate_srv_label])
    fqdn            = models.CharField(max_length=255, blank=True, null=True,\
                        validators=[_validate_srv_name])# fqdn = label + domain.name <--- see set_fqdn
    id              = models.AutoField(primary_key=True)
    target          = models.CharField(max_length=100, validators=[_validate_name])
    port            = models.PositiveIntegerField(null=False, validators=[_validate_srv_port])
    priority        = models.PositiveIntegerField(null=False, validators=[_validate_srv_priority])
    weight          = models.PositiveIntegerField(null=False, validators=[_validate_srv_weight])

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
        unique_together = ('label', 'domain', 'target', 'port', 'priority', 'weight')

    def delete(self, *args, **kwargs):
        super(SRV, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(SRV, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s %s %s %s %s %s" % (self.fqdn, 'IN', 'SRV', \
                                    self.priority,self.weight, self.port, self.target)

    def __repr__(self):
        return "<%s>" % (str(self))

    def set_fqdn(self):
        try:
            if self.label == '':
                self.fqdn = self.domain.name
            else:
                self.fqdn = "%s.%s" % (self.label, self.domain.name)
        except ObjectDoesNotExist:
            return

