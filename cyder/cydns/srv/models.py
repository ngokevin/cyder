from django.db import models
from cyder.cydns.domain.models import Domain
from cyder.cydns.common.models import CommonRecord
from cyder.cydns.cydns import InvalidRecordNameError, RecordExistsError, _validate_name
from cyder.cydns.cydns import _validate_label

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

    class Meta:
        db_table = 'srv'
        unique_together = ('label', 'domain', 'target', 'port', 'priority', 'weight')

    def delete(self, *args, **kwargs):
        super(SRV, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(SRV, self).save(*args, **kwargs)

    def clean( self ):
        if self.label and self.label[0] != '_':
            raise InvalidRecordNameError("Error: SRV label must start with '_'")
        _validate_label( self.label[1:] ) # Get rid of '_'
        _validate_name( self.target )
        self._validate_srv_port()
        self._validate_srv_priority()
        self._validate_srv_weight()

    def __str__(self):
        return "%s %s %s %s %s %s %s" % ( self.fqdn(), 'IN', 'SRV', \
                                    self.priority,self.weight, self.port, self.target)

    def __repr__(self):
        return "<%s>" % (str(self))

    def fqdn(self):
        return str(self.label)+"."+self.domain.name


    def _validate_srv_port( self ):
        if self.port > 65535 or self.port < 0:
            raise InvalidRecordNameError("Error: SRV port must be within the 0 to 65535 range. See RFC 1035")

    def _validate_srv_priority( self ):
        if self.priority > 65535 or self.priority < 0:
            raise InvalidRecordNameError("Error: SRV priority must be within the 0 to 65535 range. See RFC 1035")

    def _validate_srv_weight( self ):
        if self.weight > 65535 or self.weight < 0:
            raise InvalidRecordNameError("Error: SRV priority must be within the 0 to 65535 range. See RFC 1035")


