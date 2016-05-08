# Currently we only support sqlite3
from db_sqlite import DbSqlite
from db_object import DbObject

# This class acts as the factory that produces database layer objects
class DbFactory():
    def __init__(self):
        pass

    # Only SQLite3 is implemented as of now
    @staticmethod
    def get_db_object(engine, connect_info):
        if engine != 'sqlite':
            print "Currently only sqlite3 is supported"
            return DbObject(connect_info)
        else:
            return DbSqlite(connect_info)

