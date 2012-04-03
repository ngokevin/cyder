.. _coding_standards:

Coding Ideas (Standards)
========================


Follow pep8::

    pip install pep8
    pep8 <all of the files!!>

Model code should have 100% statement coverage.

Before you do anything with an IP address (as a string or int) put it into the ipaddr library
functions IPv4Address and IPv6Address. This will standardize how things are formated, stored, and
displayed.
