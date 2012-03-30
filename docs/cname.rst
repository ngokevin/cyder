.. _cname:

CNAME'S (Aliases)
=================

    "Don't go overboard with CNAMEs."

    "Also, PTR records must point back to a valid A record, not a alias defined by a CNAME."

    -- `RFC 1912 <http://tools.ietf.org/html/rfc1912>`_

    "If a CNAME RR is present at a node, no other data should be present; this ensures that the data for
    a canonical name and its aliases cannot be different."

    "Domain names in RRs which point at another name should always point at the primary name and not the
    alias."

    -- `RFC 1034 <http://tools.ietf.org/html/rfc1034>`_

Some things that are not allowed::

    FOO.BAR.COM     CNAME       BEE.BAR.COM

    BEE.BAR.COM     A           128.193.1.1

    1.1.193.128     PTR         FOO.BAR.COM <-- PTR's shouldn't point to CNAMES

^


CNAME
-----
.. automodule:: cyder.cydns.cname.models
    :members:
