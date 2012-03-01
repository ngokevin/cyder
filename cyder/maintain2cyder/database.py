import ConfigParser
import MySQLdb
import sys

CONFIG_FILE = './cyder/maintain2cyder/database.cfg'

class Database:
    CONFIG_FILE = './cyder/maintain2cyder/database.cfg'

    # pass in string. Use that string to index section array and dynamically return a cursor.
    def __init__( self ):
        self.config_file = CONFIG_FILE
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def retry( self ):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    """
    Pass a string into this method identifing which database in the config
    you want to get a cursor to.

    @param  identifier -> name of databse
    @return None on mysqlerror
            None on non-existant database
            connection object
    """
    def get_connection(self, identifier):
        try:
            options = self.config.options( identifier )
        except ConfigParser.NoSectionError, e:
            sys.stderr.write(str(e) + '\n')
            return None
        try:
            connection = MySQLdb.connect(
                host=self.config.get( identifier, 'host' ),
                user=self.config.get( identifier, 'user' ),
                passwd=self.config.get( identifier, 'passwd' ),
                db=self.config.get( identifier, 'db' ))
        except MySQLdb.Error, e:
            sys.stderr.write(str(e) + '\n')
            return None

        return connection

    """
    Pretty much a wrapper for get_connection.
    @return None on error
    """
    def get_cursor( self, identifier):
        connection = self.get_connection( identifier )
        if not connection:
            sys.stderr.write("Couldn't get connection to database\n")
            return None
        try:
            cursor = connection.cursor()
        except MySQLdb.Error, e:
            sys.stderr.write(str(e + '\n'))
            return None
        return cursor

