from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.settings.local import CYDNS_BASE_URL
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import InvalidRecordNameError, RecordExistsError, _validate_name, _validate_label, _validate_ttl

class SRV( CommonRecord ):
    id              = models.AutoField(primary_key=True)
    target          = models.CharField(max_length=100)
    port            = models.PositiveIntegerField(null=False)
    priority        = models.PositiveIntegerField(null=False)
    weight          = models.PositiveIntegerField(null=False)

    def details(self):
        return  (
                    ('FQDN', self.fqdn()),
                    ('Record Type', 'SRV'),
                    ('Targer', self.target),
                    ('Port', self.port),
                    ('Priority', self.priority),
                    ('Weight', self.weight),
                )

    def get_absolute_url(self):
        return CYDNS_BASE_URL + "/srv/%s/detail" % (self.pk)

    def get_edit_url(self):
        return CYDNS_BASE_URL + "/srv/%s/update" % (self.pk)

    def get_delete_url(self):
        return CYDNS_BASE_URL + "/srv/%s/delete" % (self.pk)

    def delete(self, *args, **kwargs):
        super(SRV, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(SRV, self).save(*args, **kwargs)

    def clean( self ):
        if type(self.target) not in (type(''), type(u'')):
            raise InvalidRecordNameError("Error: target must be type str")
        if self.label and self.label[0] != '_':
            raise InvalidRecordNameError("Error: SRV label must start with '_'")
        _validate_label( self.label[1:] ) # Get rid of '_'
        _validate_name( self.target )
        _validate_srv_port( self.port )
        _validate_srv_priority( self.priority )
        _validate_srv_weight( self.weight )
        _check_exists( self )

    def __str__(self):
        return "%s %s %s %s %s %s %s" % ( self.fqdn(), 'IN', 'SRV', self.priority,self.weight, self.port, self.target)

    def fqdn(self):
        return str(self.label)+"."+self.domain.name

    class Meta:
        db_table = 'srv'

def _validate_srv_port( port ):
    if port > 65535 or port < 0:
        raise InvalidRecordNameError("Error: SRV port must be within the 0 to 65535 range. See RFC 1035")

def _validate_srv_priority( prio ):
    if prio > 65535 or prio < 0:
        raise InvalidRecordNameError("Error: SRV priority must be within the 0 to 65535 range. See RFC 1035")

def _validate_srv_weight( weight ):
    if weight > 65535 or weight < 0:
        raise InvalidRecordNameError("Error: SRV priority must be within the 0 to 65535 range. See RFC 1035")

def _check_exists( srv ):
    exist = SRV.objects.filter( label = srv.label, target = srv.target, priority = srv.priority, weight = srv.weight, port = srv.port, domain = srv.domain )
    for possible in exist:
        if possible.pk != srv.pk:
            raise RecordExistsError("Error: This SRV record already exists.")

