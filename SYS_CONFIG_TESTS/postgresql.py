import psycopg2 as pg

DBHOST          = "localhost"
DBPORT          = "5432"
DBNAME          = "simple_auth"
DBUSER          = "simple_auth"
DBPASS          = "simple_auth"

# Create a cursor and connection.
pg_conn = pg.connect(
	host            =       DBHOST,
	port            =       DBPORT,
	dbname          =       DBNAME,
	user            =       DBUSER,                                                       
	password        =       DBPASS
)
pg_cursor = pg_conn.cursor()

# Test a select.
pg_cursor.execute(
"""
select * from users;
"""
)
result = pg_cursor.fetchone()
import pprint as pp
pp.pprint(result)

# Test an insert.
pg_cursor.execute(
"""
insert into users (user_name, pass_hash) values ('testinsert', 'testinsert')
"""
)
pg_conn.commit()

# Done.
print("DONE")
