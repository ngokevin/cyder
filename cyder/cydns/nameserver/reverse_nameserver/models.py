from cyder.cydns.nameserver.models import *

class ReverseNameserver(BaseNameserver):
    """Name server for reverse domains.

    >>> ReverseNameserver(reverse_domain = reverse_domain, server = server)

    """
    reverse_domain = models.ForeignKey(ReverseDomain, null=False)

    class Meta:
        db_table = 'reverse_nameserver'
        unique_together = ('reverse_domain', 'server')

    def get_absolute_url(self):
        return "/cydns/reverse_nameserver/{0}/".format(self.pk)

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
