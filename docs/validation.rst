.. _validation:

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

.. autofunction:: cyder.cydns.validation.do_zone_validation
.. autofunction:: cyder.cydns.validation.check_for_master_delegation
.. autofunction:: cyder.cydns.validation.validate_zone_soa
.. autofunction:: cyder.cydns.validation.check_for_soa_partition
.. autofunction:: cyder.cydns.validation.find_root_domain

Name and Label Validation
-------------------------

.. autofunction:: cyder.cydns.validation.validate_label
.. autofunction:: cyder.cydns.validation.validate_domain_name
.. autofunction:: cyder.cydns.validation.validate_name
.. autofunction:: cyder.cydns.validation.validate_reverse_name

TTL Validation
--------------

.. autofunction:: cyder.cydns.validation.validate_ttl

SRV Validation
--------------

:class:`SRV` objects need special validation because of the ``_`` the precedes their names. They also have other fields like ``weight``, ``port`` and ``priority`` that need to be validated.

.. autofunction:: cyder.cydns.validation.validate_srv_port
.. autofunction:: cyder.cydns.validation.validate_srv_priority
.. autofunction:: cyder.cydns.validation.validate_srv_weight
.. autofunction:: cyder.cydns.validation.validate_srv_label
.. autofunction:: cyder.cydns.validation.validate_srv_name


MX Validation
-------------

.. autofunction:: cyder.cydns.validation.validate_mx_priority

IP type Validation
------------------

.. autofunction:: cyder.cydns.validation.validate_ip_type
