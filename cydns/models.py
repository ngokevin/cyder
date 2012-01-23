from django.db import models
import string
"""
.. module:: cydns

"""

class InvalidRecordNameError(Exception):
    """This exception is thrown when an attempt is made to create/update a record with an invlaid name."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.msg

def _validate_label( label ):
    """Run test on a record to make sure that the new name is constructed with valid syntax.

        :param label: The name to be tested.
        :type label: str
    """
    if type(label) is not type(''):
            raise InvalidRecordNameError("Error: The supplied name '%s' is not of type 'str'." % (label) )
    valid_chars = string.ascii_letters+"0123456789"+"-"
    for char in label:
        if char == '.':
            raise InvalidRecordNameError("Error: Ivalid name %s . Please do not span multiple domains when creating A records." % (label) )
        if valid_chars.find(char) < 0:
            raise InvalidRecordNameError("Error: Ivalid name %s . Character '%s' is invalid." % (label, char) )
    return
