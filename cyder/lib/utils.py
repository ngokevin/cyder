import ConfigParser

def get_config(type, field, test=False):
    """ Get values from the config file """

    config = ConfigParser.ConfigParser()
    if test:
        config.read("/etc/cyder_test.cfg")
    else:
        config.read("/etc/cyder.cfg")

    value = config.get(type, field)
    return value
