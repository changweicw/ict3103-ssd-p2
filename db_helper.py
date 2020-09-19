from pypika import Query, Table, Field


def check_login(username, password, db_cursor):
    q = Query.from_('credentials').select('*')
    query = "SELECT * FROM credentials WHERE username = %s"
    db_cursor.execute(query, (username,))
    result = db_cursor.fetchone()
    if result:
        return result
    else:
        return None
