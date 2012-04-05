from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import cyder
from cyder.cydns.domain.models import Domain, _check_TLD_condition
from cyder.cydns.models import ObjectUrlMixin
from cyder.cydns.validation import validate_label, validate_name
import pdb


class CommonRecord(models.Model, ObjectUrlMixin):
    """
    This class provides common functionality that many DNS record
    classes share.  This includes a foreign key to the ``domain`` table
    and a ``label`` CharField.  This class also inherits from the
    ``ObjectUrlMixin`` class to provide the ``get_absolute_url``,
    ``get_edit_url``, and ``get_delete_url`` functions.

    This class does validation on the ``label`` field. Call
    ``clean_all`` to trigger the validation functions. Failure to
    validate will raise a ``ValidationError``.

    If you plan on using the ``unique_together`` constraint on a Model
    that inherits from ``CommonRecord``, you must include ``domain`` and
    ``label`` explicitly if you need them to.  ``CommonRecord`` will not
    enforce uniqueness for you.

    All common records have a ``fqdn`` field. This field is updated
    every time the object is saved::

        fqdn = name + domain.name

        or if name == ''

        fqdn = domain.name

    This field makes searching for records much easier. Instead of
    looking at ``obj.label`` together with ``obj.domain.name``, you can
    just search the ``obj.fqdn`` field.

    As of commit 7b2fd19f, the build scripts do not care about ``fqdn``.
    This could change.

    "the total number of octets that represent a name (i.e., the sum of
    all label octets and label lengths) is limited to 255" - RFC 4471
    """

    domain = models.ForeignKey(Domain, null=False)
    label = models.CharField(max_length=100, blank=True, null=True,
                             validators=[validate_label])
    fqdn = models.CharField(max_length=255, blank=True, null=True,
                            validators=[validate_name])
    # fqdn = label + domain.name <--- see set_fqdn

    class Meta:
        abstract = True

    def clean(self):
        self.set_fqdn()
        self.check_TLD_condition()

    def set_fqdn(self):
        try:
            if self.label == '':
                self.fqdn = self.domain.name
            else:
                self.fqdn = "{0}.{1}".format(self.label, self.domain.name)
        except ObjectDoesNotExist:
            return

    def check_for_cname(self):
        """"If a CNAME RR is preent at a node, no other data should be
        present; this ensures that the data for a canonical name and its
        aliases cannot be different."

        -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

        Call this function in models that can't overlap with an existing
        CNAME.
        """
        CNAME = cyder.cydns.cname.models.CNAME
        if CNAME.objects.filter(fqdn=self.fqdn).exists():
            raise ValidationError("A CNAME with this name already exists.")

    def check_for_delegation(self):
        """If an object's domain is delegated it should not be able to
        be changed.  Delegated domains cannot have objects created in
        them.
        """
        if not self.domain.delegated:
            return
        if not self.pk:  # We don't exist yet.
            raise ValidationError("No objects can be created in the {0}"
                                  "domain. It is delegated."
                                  .format(self.domain.name))

    def check_TLD_condition(self):
        _check_TLD_condition(self)
