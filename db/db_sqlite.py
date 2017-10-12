from db_object import DbObject
# Database driver imports can go here
try:
    import sqlite3
except ImportError:
    pass

class DbSqlite(DbObject):
    COL_MAP = {
        "float": "real",
        "int":  "real",
        "real": "real"
    }

    def __init__(self, db_path):
        if self.initialize_db(db_path):
            self.db_capable = True
            self.db_path = db_path
        else:
            self.db_capable = False

    # Initialize the SQlite DB file if it doesn't exist
    def initialize_db(self, db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.close()
            return True
        except ImportError:
            print "Without sqlite installed we can't give Jenni a brain :("
        except Exception as e:
            error = 'Error: something went wrong initializing or connecting to the DB: {0}'.format(e)
            print >> sys.stderr, error
        return False

    def check_table_exists(self, tablename):
        if not self.db_capable:
            return False

        stmt = 'pragma table_info({0})'.format(tablename.replace('\'', '\'\''))

        result = self.exec_query('ONE', stmt)

        if result:
            return True

        return False

    # Only supports 'AND' logic right now
    def get_row(self, table, conditions, cols=['*']):
        return self._get_rows('ONE', table, conditions, cols)

    # Only supports 'AND' logic right now
    def get_rows(self, table, conditions, cols=['*']):
        return self._get_rows('ALL', table, conditions, cols)

    def _get_rows(self, fetch_mode, table, conditions, cols=['*']):
        condition_col_array = []
        value_array = []

        self._col_value_split(conditions, condition_col_array, value_array)

        stmt = 'SELECT {0} FROM {1} WHERE {2}'.format(
            ','.join(cols),
            table,
            ' AND '.join(condition_col_array)
        )

        return self.exec_query(fetch_mode, stmt, tuple(value_array))

    # If no column order is specified it takes the natural ordering
    def get_all_rows(self, table, col_order=['*']):
        stmt = 'SELECT {0} FROM {1}'.format(','.join(col_order), table)
        return self.exec_query('ALL', stmt)

    # Assumes all required columns of table are included in args
    def insert_row(self, table, args):
        stmt = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(
            table,
            ','.join(args.keys()),
            (','.join(['?'] * len(args)))
        )
        self.exec_query('NONE', stmt, tuple(args.values()))

    # Only supports 'AND' logic right now
    def update_row(self, table, updates, conditions):
        update_col_array = []
        condition_col_array = []
        value_array = []

        self._col_value_split(updates, update_col_array, value_array)
        self._col_value_split(conditions, condition_col_array, value_array)

        stmt = 'UPDATE {0} SET {1} WHERE {2}'.format(
            table,
            ','.join(update_col_array),
            ' AND '.join(condition_col_array)
        )

        self.exec_query('NONE', stmt, tuple(value_array))

    # Only supports 'AND' logic right now
    def delete_rows(self, table, conditions={}):
        col_array = []
        value_array = []
        self._col_value_split(conditions, col_array, value_array)

        stmt = 'DELETE FROM {0} WHERE {1}'.format(table, ' AND '.join(col_array))
        self.exec_query('NONE', stmt, tuple(value_array))

    def create_table(self, table, columns):
        table_args = []
        for column, column_type in columns.items():
            if column_type in self.COL_MAP:
                column_type = self.COL_MAP[column_type]
            table_args.append("{0} {1}".format(column, column_type))
        table_args_string = "({0})".format(",".join(table_args))

        stmt = 'CREATE TABLE {0} {1}'.format(table, table_args_string)
        self.exec_query('NONE', stmt)

    # Since we might be executing on different threads
    # it's easier to just make a new connections and cursor
    # execute the statement and then automatically close it out.
    #
    # The fetch mode can be one of 'ALL', 'ONE', or 'NONE', and
    # defaults to NONE. When NONE we should commit when finished.
    def exec_query(self, fetch_mode, stmt, args=()):
        if not self.db_capable:
            return

        with sqlite3.connect(self.db_path) as db_con:
            c = db_con.cursor()
            c.execute(stmt, args)
            if fetch_mode == 'ALL':
                return c.fetchall()
            elif fetch_mode == 'ONE':
                return c.fetchone()
            else:
                db_con.commit()
            c.close()

    def _col_value_split(self, column_dict, column_array, value_array):
        for column, value in column_dict.items():
            column_array.append('{0}=?'.format(column))
            value_array.append(value)

