import sqlite3

def create_connection(db_file_path):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = sqlite3.connect(db_file_path)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    c = conn.cursor()
    c.execute(create_table_sql)

if __name__ == "__main__":
    db_path = 'TempHumidity.db'
    sql_create_table = """ CREATE TABLE IF NOT EXISTS log (
        id integer PRIMARY KEY,
        rDatetime datetime NOT NULL,
        temperature real NOT NULL,
        humidity real NOT NULL); """
    # db_path = 'aircon.db'
    # sql_create_table = """ CREATE TABLE IF NOT EXISTS log (
    #     id integer PRIMARY KEY,
    #     rDatetime datetime NOT NULL,
    #     status TEXT NOT NULL); """
    conn = create_connection(db_path)
    create_table(conn, sql_create_table)