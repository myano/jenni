# Currently we only support sqlite3
from db_sqlite import DbSqlite
from db_object import DbObject
try:
    from yoyo import read_migrations, get_backend
    MIGRATE_CAPABLE = True
except ImportError:
    print "We couldn't import yoyo-migrations, please install if you'd like to be able to run migrations"
    MIGRATE_CAPABLE = False

# This class acts as the factory that produces database layer objects
class DbFactory():
    # Only SQLite3 is implemented as of now
    @staticmethod
    def get_db_object(engine, connect_string):
        if engine != 'sqlite':
            print "Currently only sqlite3 is supported"
            return DbObject(connect_string)
        else:
            return DbSqlite(connect_string)

    @staticmethod
    def run_migrations(migrations_dir, engine, connect_string):
        if not MIGRATE_CAPABLE:
            return

        full_connect_string = "{0}://".format(engine)
        if engine == 'sqlite':
            full_connect_string += "/"
        full_connect_string += connect_string

        backend = get_backend(full_connect_string)
        migrations = read_migrations(migrations_dir)
        backend.apply_migrations(backend.to_apply(migrations))

