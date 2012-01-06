VERSION = (0, 0) # following PEP 386

def get_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    return version

__version__ = get_version()


