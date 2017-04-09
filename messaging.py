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

# Redis key timeout.
# Timeout for session to remove itself after
# inactivity.
# @TODO Note: Make sure to expire every time
# you set something or else this won't work.
# need to put this in a function.
SESSION_EXPIRE_MINUTES = 30

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
Google User Send Message 		(Postgres, Redis)
----------------------------------------------------------------------------"""
# Errors:
GUSM_1 = "Unknown g_apptoken."
GUSM_2 = "Unknown user_name in session."

def GSendMessage(g_apptoken, recipient, message):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(g_apptoken)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "GUSM_1"
			response['error'] = GUSM_1 
			response = set_response_failed(response)
			return response
		session = json.loads(session)
		# Get the email address associated with this account.
		if 'user_name' in session:
			user_name = session['user_name']
		else:
			# For some reason, the username of this gitkit user
			# is not in the session. Can't procede.
			response['error_code'] = "GUSM_2"
			response['error'] = GUSM_2 
			response = set_response_failed(response)
			return response

		# @TODO Check if message is too large.

		pg_conn, pg_curs = get_pg_conn_curser()
		# Insert the session into the gitkit_native_message_inbox table.
		pg_curs.execute("""
		PREPARE SendToGitkitUser_sub1(text, text, text) AS
			INSERT INTO
				notification_messages
			(
				sender,			
				recipient,		
				message
			) VALUES ($1, $2, $3);
		EXECUTE SendToGitkitUser_sub1(%s, %s, %s);
		""",
			(
				user_name,
				recipient,
				message,
			)
		)
		pg_conn.commit()
		# Close the db connection.
		pg_conn.close()
		# Return response.
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
Send Message 				(Postgres, Redis)
----------------------------------------------------------------------------"""
# Errors:
SM_1 = "Unknown apptoken."
SM_2 = "Unknown user_name in session."

def SendMessage(apptoken, recipient, message):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(apptoken)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "SM_1"
			response['error'] = SM_2 
			response = set_response_failed(response)
			return response
		session = json.loads(session)
		# Get the email address associated with this account.
		if 'user_name' in session:
			user_name = session['user_name']
		else:
			# For some reason, the username of this gitkit user
			# is not in the session. Can't procede.
			response['error_code'] = "SM_1"
			response['error'] = SM_2 
			response = set_response_failed(response)
			return response

		# @TODO Check if message is too large.

		pg_conn, pg_curs = get_pg_conn_curser()
		# Insert the session into the gitkit_native_message_inbox table.
		pg_curs.execute("""
		PREPARE SendToGitkitUser_sub1(text, text, text) AS
			INSERT INTO
				notification_messages
			(
				sender,			
				recipient,		
				message
			) VALUES ($1, $2, $3);
		EXECUTE SendToGitkitUser_sub1(%s, %s, %s);
		""",
			(
				user_name,
				recipient,
				message,
			)
		)
		pg_conn.commit()
		# Close the db connection.
		pg_conn.close()
		# Return response.
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
Google User Read Messages 		(Postgres, Redis)
----------------------------------------------------------------------------"""
# Errors:
GRM_1 = "Unknown g_apptoken."
GRM_2 = "Unknown user_name in session."

def GReadMessages(g_apptoken, chat_partner, max_messages):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(g_apptoken)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "GRM_1"
			response['error'] = GRM_1 
			response = set_response_failed(response)
			return response
		session = json.loads(session)
		# Get the email address associated with this account.
		if 'user_name' in session:
			user_name = session['user_name']
		else:
			# For some reason, the username of this gitkit user
			# is not in the session. Can't procede.
			response['error_code'] = "GRM_2"
			response['error'] = GRM_2 
			response = set_response_failed(response)
			return response

		# @TODO Check if message is too large.

		pg_conn, pg_curs = get_pg_conn_curser()
		# Insert the session into the gitkit_native_message_inbox table.
		pg_curs.execute("""
		PREPARE ReadAllMessages_sub1(text, text, text, text, integer) AS
			SELECT 
				message,
				read,
				TO_CHAR(creation_timestamp, 'MM-DD-YYYY HH24:MI:SS'),			
				sender,
				id
			FROM 
				notification_messages
			WHERE
				(sender = $1
					AND
				recipient = $2)  
			OR
				(sender = $3	
					AND
				recipient = $4)
			ORDER BY creation_timestamp DESC 
			LIMIT $5;
		EXECUTE ReadAllMessages_sub1(%s, %s, %s, %s, %s);
		""",
			(
				user_name,
				chat_partner,
				chat_partner,
				user_name,
				max_messages,
			)
		)
 		result = pg_curs.fetchall()
		# If there are no messages, send response back with no empty array.
		if len(result) == 0:
			response['messages'] = [] 
			response = set_response_success(response)
			return response

		message_ids = []
		messages = []
		for row in result:
			message = {}
			message['message'] = row[0]
			message['read'] = row[1]
			message['date'] = row[2]
			if row[3] == user_name:
				message['reader_is_sender'] = True 
			else:
				message['reader_is_sender'] = False
			message['sender'] = row[3]
			messages.append(message)
			message_ids.append(row[4])
		# Mark messages as read. This doesn't need to be a
		# prepared statement because the message ids are coming
		# from the database.
		update_read_messages_sql = """
		UPDATE
			notification_messages
		SET
			read = True 
		WHERE
			id IN (%s);
		""" % (
			','.join(str(message_id) for message_id in message_ids)
		)
		pg_curs.execute(update_read_messages_sql)
		pg_conn.commit()
		# Close the db connection.
		pg_conn.close()
		# Return response.
		response['messages'] = messages
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
Read Messages 				(Postgres, Redis)
----------------------------------------------------------------------------"""
# Errors:
RM_1 = "Unknown apptoken."
RM_2 = "Unknown user_name in session."

def ReadMessages(apptoken, chat_partner, max_messages):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(apptoken)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "RM_1"
			response['error'] = RM_1 
			response = set_response_failed(response)
			return response
		session = json.loads(session)
		# Get the email address associated with this account.
		if 'user_name' in session:
			user_name = session['user_name']
		else:
			# For some reason, the username of this gitkit user
			# is not in the session. Can't procede.
			response['error_code'] = "RM_2"
			response['error'] = RM_2 
			response = set_response_failed(response)
			return response

		# @TODO Check if message is too large.

		pg_conn, pg_curs = get_pg_conn_curser()
		# Insert the session into the gitkit_native_message_inbox table.
		pg_curs.execute("""
		PREPARE ReadAllMessages_sub1(text, text, text, text, integer) AS
			SELECT 
				message,
				read,
				TO_CHAR(creation_timestamp, 'MM-DD-YYYY HH24:MI:SS'),			
				sender,
				id
			FROM 
				notification_messages
			WHERE
				(sender = $1
					AND
				recipient = $2)  
			OR
				(sender = $3	
					AND
				recipient = $4)
			ORDER BY creation_timestamp DESC 
			LIMIT $5;
		EXECUTE ReadAllMessages_sub1(%s, %s, %s, %s, %s);
		""",
			(
				user_name,
				chat_partner,
				chat_partner,
				user_name,
				max_messages,
			)
		)
 		result = pg_curs.fetchall()
		# If there are no messages, send response back with no empty array.
		if len(result) == 0:
			response['messages'] = [] 
			response = set_response_success(response)
			return response

		message_ids = []
		messages = []
		for row in result:
			message = {}
			message['message'] = row[0]
			message['read'] = row[1]
			message['date'] = row[2]
			if row[3] == user_name:
				message['reader_is_sender'] = True 
			else:
				message['reader_is_sender'] = False
			message['sender'] = row[3]
			messages.append(message)
			message_ids.append(row[4])
		# Mark messages as read. This doesn't need to be a
		# prepared statement because the message ids are coming
		# from the database.
		update_read_messages_sql = """
		UPDATE
			notification_messages
		SET
			read = True 
		WHERE
			id IN (%s);
		""" % (
			','.join(str(message_id) for message_id in message_ids)
		)
		pg_curs.execute(update_read_messages_sql)
		pg_conn.commit()
		# Close the db connection.
		pg_conn.close()
		# Return response.
		response['messages'] = messages
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		pg_conn.close()
		# Return default failure response.
		response = set_response_failed(response)
		return response

# print(GSendMessage("g_bcqqyhnkrdgcwprzrwmjvcmkwobbi", "example_user@gmail.com", "Sub biiiiich"))
# print(GReadMessages("g_nbkmxcxmwpshmdpfwomxzkmhnutki", "example_user@gmail.com", 10))
# print(SendMessage("ecasdfqvepmfpwmzzmrqmcbcsvtwqwdrk", "gitkit_user@gmail.com", "test from example to gitkit_user"))
# print(ReadMessages("ecqvepmfpwmzzmrqmcbcsvtwqwdrk", "example_user@gmail.com", 10))
