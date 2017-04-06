import redis
import psycopg2 as pg
import bcrypt
import random
import string
import datetime
import json

DBHOST 		= "localhost"
DBPORT 		= "5432"
DBNAME 		= "simple_auth"
DBUSER 		= "simple_auth"
DBPASS 		= "simple_auth"

REDISHOST 	= "localhost"
REDISPORT 	= 6379

ADMIN_KEY = "ADMIN_KEY"

UE = "Unknown Error"

def get_redis_conn():
	redis_conn = redis.StrictRedis(
		host 		= 	REDISHOST,
		port		= 	REDISPORT,
		db		=	0
	)
	return redis_conn 

def get_pg_conn_curser():
	pg_conn = pg.connect(
		host 		=	DBHOST,
		port		=	DBPORT,
		dbname		=	DBNAME,
		user		=	DBUSER,
		password	=	DBPASS
	)
	pg_cursor = pg_conn.cursor()
	return pg_conn, pg_cursor

def log_auth_exception(exception):
	print(exception)

def get_default_response():
	response = {}
	response['success'] = False 
	response['error_code'] = "UE"
	response['error'] = UE
	return response

def set_response_failed(response):
	# Return a resonse only with a status of flase and the error and the
	# error_code.
	new_response = {}
	new_response['error'] = response['error']
	new_response['error_code'] = response['error_code']
	new_response['success'] = False
	return new_response

def set_response_success(response):
	# Remove error and error_code from response. Finally set success
	# to true.
	if response['error'] is not None:
		response.pop('error')
	if response['error_code'] is not None:
		response.pop('error_code')
	response['success'] = True
	return response

def generate_cookie():
	return ''.join(random.choice(string.lowercase) for i in range(29))

"""----------------------------------------------------------------------------
Log User In				(Postgres, Redis)
----------------------------------------------------------------------------"""
# Errors:
LUI_1 = "User already logged in."
LUI_2 = "Unknown user name for login."
LUI_3 = "Incorrect password for login."

def LogUserIn(user_name, password):
	response = get_default_response()
	try:
		pg_conn, pg_curs = get_pg_conn_curser()
		# First make sure no session exists for this username.
		# Since we don't have a cookie, we need to check the
		# table cookies_by_user_name.
		pg_curs.execute("""
		PREPARE LogUserIn_sub1(text) AS
			SELECT
				cookie
			FROM 
				cookies_by_username	
			WHERE
				user_name = $1;
		EXECUTE LogUserIn_sub1(%s);
		""",
			(
				user_name,
			)
		)
		result = pg_curs.fetchone()
		if result is not None:
			# Close the db connection.
			pg_conn.close()
			# User already logged in.
			# Return the cookie as if you are loggin them in
			# for the first time.
			cookie = result[0]

			# Prepare the response.
			response['cookie'] = cookie
			response = set_response_success(response)

			# Return response.
			return response
		# Next, get the username and password for the user.
		pg_curs.execute("""
		PREPARE LogUserIn_sub2(text) AS
			SELECT
				pass_hash	
			FROM
				users
			WHERE
				user_name = $1;
		EXECUTE LogUserIn_sub2(%s);
		""",
			(
				user_name,
			)
		)
		result = pg_curs.fetchone()
		if result is None:
			# Close the db connection.
			pg_conn.close()
			# Unknown user name for login.
			response['error_code'] = "LUI_2"
			response['error'] = LUI_2
			response = set_response_failed(response)
			return response
		# Check the password hash against what the user gave
		# as a password.
		hashed = result[0]
		if bcrypt.hashpw(password.encode('utf8'), hashed) != hashed:
			# Close the db connection.
			pg_conn.close()
			# Incorrect password for login.
			response['error_code'] = "LUI_3"
			response['error'] = LUI_3
			response = set_response_failed(response)
			return response
		# If there is no mismatch, log the user into the
		# cookies_by_username table and into the redis
		# session store.

		# Build the session.
		cookie = generate_cookie()
		session = {}
		session['user_name'] = user_name
		session['creation_timestamp'] = str(datetime.datetime.now())
		session['cookie'] = cookie

		# Set the session in postgres so that we have a relational
		# way to look it up by username.
		pg_curs.execute("""
                PREPARE LogUserIn_sub3(text, text) AS
			INSERT INTO
				cookies_by_username
			(
				cookie,
				user_name
			)
			VALUES ($1, $2);
                EXECUTE LogUserIn_sub3(%s, %s);
		""",
			(
				cookie,
				user_name,
			)
		)
		pg_conn.commit()

		# Set the session in Redis so we can look it up by cookie
		# hella fast.
		redis_conn = get_redis_conn()
		redis_conn.set(cookie, json.dumps(session))

		# Prepare the response.
		response['cookie'] = cookie
		response = set_response_success(response)

		# Close the db connection.
		pg_conn.close()
		# Return response.
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Log User Out				(Postgres, Redis)
----------------------------------------------------------------------------"""

def LogUserOut(cookie):
	response = get_default_response()
	try:
		# Remove the session from the cookie_by_username tables.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE LogUserOut_sub1(text) AS
			DELETE FROM
				cookies_by_username
			WHERE
				cookie = $1;
		EXECUTE LogUserOut_sub1(%s);
		""",
			(
				cookie,
			)
		)
		# Commit the query.
		pg_conn.commit()
		# Close postgres connection.
		pg_conn.close()
		# Remove the session from redis.
		redis_conn = get_redis_conn()
		redis_conn.delete(cookie)
		# Return logout success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Forced User Log Out			(Postgres, Redis)
----------------------------------------------------------------------------"""
FLOU_1 = "Incorrect admin key."

def ForceLogUserOut(user_name, admin_key):
	response = get_default_response()
	try:
		# Ensure the admin key is correct.
		if admin_key != ADMIN_KEY:
			response['error_code'] = "FLOU_1"
			response['error'] = FLOU_1 
			response = set_response_failed(response)
			return response

		pg_conn, pg_curs = get_pg_conn_curser()
		# Look up the cookie for the username.
		pg_curs.execute("""
		PREPARE ForceLogUserOut_sub1(text) AS
			SELECT
				cookie
			FROM 
				cookies_by_username
			WHERE
				user_name = $1;
		EXECUTE ForceLogUserOut_sub1(%s);
		""",
			(
				user_name,
			)
		)
		result = pg_curs.fetchone()
		# If the cookie exists, remove the user from the 
		# cookies by username table.
		if result is not None:
			cookie = result[0]
			pg_curs.execute("""
			PREPARE ForceLogUserOut_sub2(text) AS
				DELETE FROM
					cookies_by_username
				WHERE
					cookie = $1;
			EXECUTE ForceLogUserOut_sub2(%s);
			""",
				(
					cookie,
				)
			)
			# Commit the query.
			pg_conn.commit()
			# Remove the session from redis.
			redis_conn = get_redis_conn()
			redis_conn.delete(cookie)
		# Close postgres connection.
		pg_conn.close()
		# Return logout success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Set Session Variable 			(Redis)
----------------------------------------------------------------------------"""
SSV_1 = "Unknown cookie."

def SetSessionVars(cookie, session_vars):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(cookie)
		if session is None:
			# Unknown cookie.
			# The user is not authenticated.
			response['error_code'] = "SSV_1"
			response['error'] = SSV_1
			response = set_response_failed(response)
			return response
		# Unmarshal the session, add the new values, re-marshal, and
		# store back in redis.			

		# Unmarshal session.
		session = json.loads(session)
		# Set new variables.
		for key, value in session_vars.iteritems():
			session[key] = value
		# Remarshal session.
		session = json.dumps(session)
		# Store in redis.
		redis_conn.set(cookie, session)
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Unset Session Variable 			(Redis)
----------------------------------------------------------------------------"""
USV_1 = "Unknown cookie."

def UnsetSessionVars(cookie, session_vars):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(cookie)
		if session is None:
			# Unknown cookie.
			# The user is not authenticated.
			response['error_code'] = "USV_1"
			response['error'] = USV_1
			response = set_response_failed(response)
			return response
		# Unmarshal the session, add the new values, re-marshal, and
		# store back in redis.			

		# Unmarshal session.
		session = json.loads(session)
		# Remove session keys
		for key in session_vars:
			session.pop(key, None)
		# Remarshal session.
		session = json.dumps(session)
		# Store in redis.
		redis_conn.set(cookie, session)
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Read Session Variable 			(Redis)
----------------------------------------------------------------------------"""
RSV_1 = "Unknown cookie."

def ReadSessionVars(cookie, session_keys):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(cookie)
		if session is None:
			# Unknown cookie.
			# The user is not authenticated.
			response['error_code'] = "RSV_1"
			response['error'] = RSV_1
			response = set_response_failed(response)
			return response
		# Unmarshal the session, find the values you need
		# and return them.

		# Get the session from redis.
		redis_conn.get(cookie)
		# Unmarshal session.
		session = json.loads(session)
		# Generate return set.
		return_set = {}
		# Find the keys we searched for. 
		for key, value in session.iteritems():
			if key in session_keys:
				return_set[key] = value
		# Set NULL for keys we didn't find.
		for key in session_keys:
			if key not in return_set:
				return_set[key] = "NULL"
		# Add the return to the reponse.
		response['session_variables'] = return_set 
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Register User				(Postgres)
----------------------------------------------------------------------------"""
RU_1 = "User already exists."

def RegisterUser(user_name, password):
	response = get_default_response()
	try:
		pg_conn, pg_curs = get_pg_conn_curser()
		# First make sure no user with that user name exists.
		pg_curs.execute("""
		PREPARE RegisterUser_sub1(text) AS
			SELECT
				count(*)
			FROM 
				users
			WHERE
				user_name = $1;
		EXECUTE RegisterUser_sub1(%s);
		""",
			(
				user_name,
			)
		)
		result = pg_curs.fetchone()
		count = result[0]
		if count != 0:
			# Close the db connection.
			pg_conn.close()
			# User already exists.
			response['error_code'] = "RU_1"
			response['error'] = RU_1
			response = set_response_failed(response)
			return response

		# If there is no existing user, add the user to the users
		# tables.

		# Hash their password.
		hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

		pg_curs.execute("""
		PREPARE RegisterUser_sub2(text, text) AS
			INSERT INTO
				users
			(
				user_name,
				pass_hash	
			)
			VALUES ($1, $2);
		EXECUTE RegisterUser_sub2(%s, %s);
		""",
			(
				user_name,
				hashed
			)
		)
		pg_conn.commit()
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Unregister User				(Postgres)
----------------------------------------------------------------------------"""
UU_2 = "Unauthorized request."

def UnregisterUser(user_name, cookie):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(cookie)
		if session is None:
			# Unknown cookie.
			# The user is not authenticated.

			# See if there is an admin_key.
			if cookie != ADMIN_KEY:
				# The admin key was attempted but is
				# incorrect.  This not an authenticated 
				# request.
				response['error_code'] = "UU_2"
				response['error'] = UU_2 
				response = set_response_failed(response)
				return response

		# If the user is authenticated with a session or
		# the admin key matches, delete the user.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE UnregisterUser_sub1(text) AS
			DELETE FROM
				users
			WHERE
				user_name = $1;
		EXECUTE UnregisterUser_sub1(%s);
		""",
			(
				user_name,
			)
		)
		# Commit the transaction.
		pg_conn.commit()
		# Close postgres connection.
		pg_conn.close()
		# If the user was logged in, remove the session from redis.
		if session is not None:
			redis_conn = get_redis_conn()
			redis_conn.delete(cookie)
		# Return unregistration success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Register Role			(Postgres)
----------------------------------------------------------------------------"""
RR_1 = "Invalid admin key."
RR_2 = "Role already exists."

def RegisterRole(admin_key, role_name):
	response = get_default_response()
	try:
		if admin_key != ADMIN_KEY:
			# The admin key was attempted but is
			# incorrect.  This not an authenticated 
			# request.
			response['error_code'] = "RR_1"
			response['error'] = RR_1 
			response = set_response_failed(response)
			return response
		# Just register the role. If it already exists, this will
		# be caught in the exception.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE RegisterRole_sub1(text) AS
			INSERT INTO
				roles
			(
				role_name
			)
			VALUES ($1);
		EXECUTE RegisterRole_sub1(%s);
		""",
			(
				role_name,
			)
		)
		pg_conn.commit()
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Try to parse exceptions.
		if "already exists" in str(ex):
			# The role already exists.
			response['error_code'] = "RR_2"
			response['error'] = RR_2 
			response = set_response_failed(response)
			return response
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Associate User Role			(Postgres)
----------------------------------------------------------------------------"""
AUR_1 = "Invalid admin key."
AUR_2 = "User does not exists."
AUR_3 = "Role does not exists."
AUR_4 = "User role association already exists."

def AssociateUserRole(admin_key, user_name, role_name):
	response = get_default_response()
	try:
		if admin_key != ADMIN_KEY:
			# The admin key was attempted but is
			# incorrect.  This not an authenticated 
			# request.
			response['error_code'] = "AUR_1"
			response['error'] = AUR_1 
			response = set_response_failed(response)
			return response
		# Just register the role. If it already exists, this will
		# be caught in the exception.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE AssociateUserRole_sub1(text, text) AS
			INSERT INTO
				user_roles
			(
				user_name,
				role_name
			)
			VALUES ($1, $2);
		EXECUTE AssociateUserRole_sub1(%s, %s);
		""",
			(
				user_name,
				role_name,	
			)
		)
		pg_conn.commit()
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Try to parse exceptions.
		if "already exists" in str(ex):
			# The user role already exists.
			response['error_code'] = "AUR_4"
			response['error'] = AUR_4 
			response = set_response_failed(response)
			return response
		if ("user_name" in str(ex)) and ("violates foreign key constraint" in str(ex)):
			# Invlalid user fk.
			response['error_code'] = "AUR_2"
			response['error'] = AUR_2 
			response = set_response_failed(response)
			return response
		if ("role_name" in str(ex)) and ("violates foreign key constraint" in str(ex)):
			# Invlalid role fk.
			response['error_code'] = "AUR_3"
			response['error'] = AUR_3 
			response = set_response_failed(response)
			return response
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Unregister Role			(Postgres)
----------------------------------------------------------------------------"""
UR_1 = "Invalid admin key."

def UnregisterRole(admin_key, role_name):
	response = get_default_response()
	try:
		if admin_key != ADMIN_KEY:
			# The admin key was attempted but is
			# incorrect.  This not an authenticated 
			# request.
			response['error_code'] = "UR_1"
			response['error'] = UR_1 
			response = set_response_failed(response)
			return response
		# Just register the role. If it already exists, this will
		# be caught in the exception.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE UnregisterRole_sub1(text) AS
			DELETE FROM
				roles
			WHERE
				role_name = $1;
		EXECUTE UnregisterRole_sub1(%s);
		""",
			(
				role_name,	
			)
		)
		pg_conn.commit()
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Disassociate User Role			(Postgres)
----------------------------------------------------------------------------"""
DUR_1 = "Invalid admin key."

def DisassociateUserRole(admin_key, user_name, role_name):
	response = get_default_response()
	try:
		if admin_key != ADMIN_KEY:
			# The admin key was attempted but is
			# incorrect.  This not an authenticated 
			# request.
			response['error_code'] = "DUR_1"
			response['error'] = DUR_1 
			response = set_response_failed(response)
			return response
		# Just unregister the user role. If it doesnt already exists, 
		# the state of the application will still be the same as what
		# the user expects it to be after the command.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE DisassociateUserRole_sub1(text, text) AS
			DELETE FROM
				user_roles
			WHERE
				user_name = $1
			AND
				role_name = $2;
		EXECUTE DisassociateUserRole_sub1(%s, %s);
		""",
			(
				user_name,
				role_name,	
			)
		)
		pg_conn.commit()
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response




###############################################################################
"""----------------------------------------------------------------------------

	HANDLING GOOGLE IDENTITY TOOLKIT:

----------------------------------------------------------------------------"""
###############################################################################




"""----------------------------------------------------------------------------
Handle Only Gitkit Token 		(Postgres, Redis)
----------------------------------------------------------------------------"""
# Errors:
# This should never happen.

def HandleOnlyGitkitToken(email_address):
	response = get_default_response()
	try:
		pg_conn, pg_curs = get_pg_conn_curser()
		# Inser the record into google users. Creation
		# timestamp will be set on creation, insert again
		# on reinsert, if confluct occurs, last login will
		# be the only field updated. 
		pg_curs.execute("""
		PREPARE HandleOnlyGitkitToken_sub1(text) AS
			INSERT INTO
				google_users
			(
				email_address
			)
			VALUES ($1)
			ON CONFLICT (email_address)
			DO UPDATE
			SET
				last_login = NOW();
		EXECUTE HandleOnlyGitkitToken_sub1(%s);
		""",
			(
				email_address,
			)
		)
		pg_conn.commit()

		# Build the session.
		g_apptoken = "g_" + generate_cookie() # Actually a token for google only users.
		session = {}
		session['user_name'] = email_address 
		session['creation_timestamp'] = str(datetime.datetime.now())
		session['g_apptoken'] = g_apptoken 

		# Set the session in Redis so we can look it up by g_apptoken (a cookie)
		# hella fast.
		redis_conn = get_redis_conn()
		redis_conn.set(g_apptoken, json.dumps(session))

		# Insert the user session (g_apptoken) into
		# the g_apptokens_by_email_address table.
		pg_curs.execute("""
		PREPARE HandleOnlyGitkitToken_sub2(text, text, text) AS
			INSERT INTO
				g_apptokens_by_email_address
			(
				email_address,
				g_apptoken
			)
			VALUES ($1, $2)
			ON CONFLICT (email_address)
			DO UPDATE
			SET
				g_apptoken = $3;
		EXECUTE HandleOnlyGitkitToken_sub2(%s, %s, %s);
		""",
			(
				email_address,
				g_apptoken,
				g_apptoken,
			)
		)
		pg_conn.commit()

		# Prepare the response.
		response['g_apptoken'] = g_apptoken 
		response = set_response_success(response)

		# Close the db connection.
		pg_conn.close()
		# Return response.
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Read Gitkit User Session 		(Redis)
----------------------------------------------------------------------------"""
RGUS_1 = "Unknown g_apptoken."

def ReadGitkitUserSessionVars(g_apptoken, session_keys):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(g_apptoken)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "RSV_1"
			response['error'] = RGUS_1 
			response = set_response_failed(response)
			return response
		# Unmarshal the session, find the values you need
		# and return them.

		# Get the session from redis.
		redis_conn.get(g_apptoken)
		# Unmarshal session.
		session = json.loads(session)
		# Generate return set.
		return_set = {}
		# Find the keys we searched for. 
		for key, value in session.iteritems():
			if key in session_keys:
				return_set[key] = value
		# Set NULL for keys we didn't find.
		for key in session_keys:
			if key not in return_set:
				return_set[key] = "NULL"
		# Add the return to the reponse.
		response['session_variables'] = return_set 
		# Return success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Gitkit User Log Out			(Postgres, Redis)
----------------------------------------------------------------------------"""

def GitkitUserLogOut(g_apptoken):
	response = get_default_response()
	try:
		# Remove from the g_apptokens_by_email_address table.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE GitkitUserLogOut_sub1(text) AS
			DELETE FROM
				g_apptokens_by_email_address
			WHERE
				g_apptoken = $1;
		EXECUTE GitkitUserLogOut_sub1(%s);
		""",
			(
				g_apptoken,	
			)
		)
		pg_conn.commit()
		# Remove the session from redis.
		redis_conn = get_redis_conn()
		redis_conn.delete(g_apptoken)
		# Return logout success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

"""----------------------------------------------------------------------------
Force Gitkit User Log Out		(Postgres, Redis)
----------------------------------------------------------------------------"""
FGULO_1 = "Invalid admin key."

def ForceGitkitUserLogOut(email_address, admin_key):
	response = get_default_response()
	try:
		# Ensure the admin key is correct.
		if admin_key != ADMIN_KEY:
			response['error_code'] = "FGULO_1"
			response['error'] = FGULO_1 
			response = set_response_failed(response)
			return response

		pg_conn, pg_curs = get_pg_conn_curser()
		# Look up the g_apptoken for the email_address.
		pg_curs.execute("""
		PREPARE ForceGitkitUserLogOut_sub1(text) AS
			SELECT
				g_apptoken
			FROM 
				g_apptokens_by_email_address
			WHERE
				email_address = $1;
		EXECUTE ForceGitkitUserLogOut_sub1(%s);
		""",
			(
				email_address,
			)
		)
		result = pg_curs.fetchone()
		# If the g_apptoken exists, remove the user from the 
		# g_apptoken by email_address table.
		if result is not None:
			g_apptoken = result[0]
			pg_curs.execute("""
			PREPARE ForceGitkitUserLogOut_sub2(text) AS
				DELETE FROM
					g_apptokens_by_email_address
				WHERE
					g_apptoken = $1;
			EXECUTE ForceGitkitUserLogOut_sub2(%s);
			""",
				(
					g_apptoken,
				)
			)
			# Commit the query.
			pg_conn.commit()
			# Remove the session from redis.
			redis_conn = get_redis_conn()
			redis_conn.delete(g_apptoken)
		# Close postgres connection.
		pg_conn.close()
		# Return logout success.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response


# print(LogUserIn('user_name_1','super secret shit'))
# print(LogUserOut('ulmaskkvtvjvxlixhdizzmbmhzigh'))
# print(ForceLogUserOut("example_user@gmail.com", ADMIN_KEY))
# print(SetSessionVars('hmpnorcjnlzqsppnmwoymnrerheqq', {'key': 'value', 'key1': 'value1'}))
# print(UnsetSessionVars('hmpnorcjnlzqsppnmwoymnrerheqq', {'key': 'value', 'key1': 'value1'}))
# print(ReadSessionVariables('hmpnorcjnlzqsppnmwoymnrerheqq', ['creation_timestamp', 'cookie', 'asdfasdf']))
# print(RegisterUser('new_user', 'new_password'))
# print(RegisterRole(ADMIN_KEY, 'some_role'))
# print(UnregisterUser('someuser', None, "ADMIN_KEY"))
# print(AssociateUserRole(ADMIN_KEY, "test", "some_role"))
# print(DisassociateUserRole(ADMIN_KEY, "test", "some_role"))
# print(UnregisterRole(ADMIN_KEY, "some_role"))
# print(HandleOnlyGitkitToken("zndr.k.94@gmail.com"))
# print(ReadGitkitUserSessionVars("g_kpnaojystvyykcuoousntdkdxszlk", ['creation_timestamp', 'cookie', 'asdfasdf']))
# print(GitkitUserLogOut("g_kpnaojystvyykcuoousntdkdxszlk"))
# print(ForceGitkitUserLogOut("zndr.k.94@gmail.com", "ADMIN_KEY"))
