.. _validators:

Validation
==========

Validation happens all over the place. These are validation functions that ended up in the same file.

Domain/ReverseDomain Validation
-------------------------------

Both :ref:`reverse_domain`\s and Forward :ref:`domain`\s have similar functions that need to be called to validate
state in the database. Unfortunately naming convention stops extremely generic code from being written. These
functions are not extremely generic; these functions are mildly of generic.

The functions in this file use the name ``domain`` to mean both ``reverse_domain``  and forward
``domain``.

Use the function ``do_zone_validation`` in model code.

.. automodule:: cyder.cydns.validation
    :members: do_zone_validation, check_for_master_delegation, validate_zone_soa, check_for_soa_partition, find_root_domain

Name and Label Validation
-------------------------

.. automodule:: cyder.cydns.validation
    :members: validate_label, validate_domain_name, validate_name, validate_reverse_name

TTL Validation
--------------

.. automodule:: cyder.cydns.validation
    :members: validate_ttl

SRV Validation
--------------

:class:`SRV` objects need special validation because of the ``_`` the precedes their names. They also have other fields like ``weight``, ``port`` and ``priority`` that need to be validated.

.. automodule:: cyder.cydns.validation
    :members: validate_srv_port, validate_srv_priority, validate_srv_weight, validate_srv_label, validate_srv_name


MX Validation
-------------

.. automodule:: cyder.cydns.validation
    :members: validate_mx_priority

IP type Validation
------------------

.. automodule:: cyder.cydns.validation
    :members: validate_ip_type
