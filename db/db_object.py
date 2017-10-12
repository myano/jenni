class DbObject():
    def __init__(self, connect_info):
        self._print_override_error('__init__')
        self.db_capable = False

    # In the case of SQLite connect info will be a path
    # whereas in the case of MySQL it will be a dict.
    def initialize_db(self, connect_info):
        self._print_override_error('initialize_db')

    def check_table_exists(self, tablename):
        self._print_override_error('check_table_exists')

    def get_row(self, table, args=()):
        self._print_override_error('get_row')

    def get_rows(self, table, args=()):
        self._print_override_error('get_rows')

    def get_all_rows(self, table, col_order=['*']):
        self._print_override_error('get_all_rows')

    def insert_row(self, table, args=()):
        self._print_override_error('insert_row')

    def update_row(self, table, updates, conditions):
        self._print_override_error('update_row')

    def delete_rows(self, table, args=()):
        self._print_override_error('delete_rows')

    def create_table(self, table, columns):
        self._print_override_error('create_table')

    def exec_query(self, fetch_mode, stmt, args=()):
        self._print_override_error('exec_query')

    def _print_override_error(self, func):
        error = "You must implement '{0}' within your DAL".format(func)
        print >> stderr, error

