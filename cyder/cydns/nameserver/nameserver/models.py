from cyder.cydns.nameserver.models import *


class Nameserver(BaseNameserver):
    """Name server for forward domains::

    >>> Nameserver(domain = domain, server = server)

    """
    domain = models.ForeignKey(Domain, null=False)
    # "If the name server does lie within the domain it should have a
    # corresponding A record."
    glue = models.ForeignKey(AddressRecord, null=True, blank=True)

    class Meta:
        db_table = 'nameserver'
        unique_together = ('domain', 'server')

    def details(self):
        details = [
            ('Server', self.server),
            ('Domain', self.domain.name),
            ('Glue', self.glue),
        ]
        return tuple(details)

    def clean(self):
        super(Nameserver, self).clean()

        if not self._needs_glue():
            self.glue = None
        else:
            # Try to find any glue record. It will be the first elligible
            # A record found.
            glue_label = self.server.split('.')[0]  # foo.com -> foo
            glue = AddressRecord.objects.filter(label=glue_label,
                                                domain=self.domain)
            if not glue:
                raise ValidationError(
                    "NS needs glue record. Create a glue "
                    "record for the server before creating "
                    "the NS record."
                )
            else:
                self.glue = glue[0]

    def save(self, *args, **kwargs):
        self.full_clean()
        self.domain.dirty = True
        self.domain.save()
        super(Nameserver, self).save(*args, **kwargs)

    def __repr__(self):
        return "<Forward '{0}'>".format(str(self))

    def __str__(self):
        return "{0} {1} {2}".format(self.domain.name, 'NS', self.server)

    def _needs_glue(self):
        # Replace the domain portion of the server with "".
        # if domain == foo.com and server == ns1.foo.com.
        #       ns1.foo.com --> ns1
        try:
            possible_label = self.server.replace("." + self.domain.name, "")
        except ObjectDoesNotExist:
            return False

        if possible_label == self.server:
            return False
        try:
            validate_label(possible_label)
        except ValidationError:
            # It's not a valid label
            return False
        return True
