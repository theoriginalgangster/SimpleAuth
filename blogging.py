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
Create New Post				(Postgres)
----------------------------------------------------------------------------"""
CNP_1 = "Unrecognized app_token."
CNP_2 = "Post with that title already exists."
CNP_3 = "Unknown author. Author must have an admin account."

def CreateNewPost(app_token, title, author, publication_timestamp, main_image_url, content, tags, category, hidden):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(app_token)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "CNP_1"
			response['error'] = CNP_1 
			response = set_response_failed(response)
			return response
		session = json.loads(session)

		pg_conn, pg_curs = get_pg_conn_curser()
		# Insert the post.
		pg_curs.execute("""
		PREPARE CreateNewPost_sub1(text, text, text, text, text, text, boolean) AS
			INSERT INTO
				blog_posts
			(
				title,
				author,
				publication_timestamp,
				main_image_url,
				content,
				category,
				hidden
			) VALUES ($1, $2, to_timestamp($3, 'dd-mm-yyyy hh24:mi:ss'), $4, $5, $6, $7);
		EXECUTE CreateNewPost_sub1(%s, %s, %s, %s, %s, %s, %s);
		""",
			(
				title,
				author,
				publication_timestamp,
				main_image_url,
				content,
				category,
				hidden,
			)
		)
		pg_conn.commit()
		pg_conn.close()
		# Associate all the tags.
		# @TODO Figure out what the hell is going on with prepared
		# statements already existing so I don't have to open a new
		# db connection to associate tags.
		for tag in tags:
			pg_conn, pg_curs = get_pg_conn_curser()
			pg_curs.execute("""
			PREPARE CreateNewPost_sub1(text, text) AS
				INSERT INTO
					blog_post_tags
				(
					post_title,
					tag
				) VALUES ($1, $2);
			EXECUTE CreateNewPost_sub1(%s, %s);
			""",
				(
					title,
					tag,
				)
			)
			pg_conn.commit()
			pg_conn.close()
		# Return response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Check for foreign key errors.
		if ("title" in str(ex)) and ("already exists" in str(ex)):
			response['error_code'] = "CNP_2"
			response['error'] = CNP_2
			response = set_response_failed(response)
			return response
		if ("author" in str(ex)) and ("not present" in str(ex)):
			response['error_code'] = "CNP_3"
			response['error'] = CNP_3
			response = set_response_failed(response)
			return response
		# Return default failure response.
		response = set_response_failed(response)
		return response

# print(CreateNewPost("ecqvepmfpwmzzmrqmcbcsvtwqwdrk", "example_title", "example_user@gmail.com", "2017-04-05 21:46:05.243873", "example_main_image_url", "example_content", ["example_tag_1", "exapmle_tag_2"], "example_category", False))

"""----------------------------------------------------------------------------
Edit Post				(Postgres)
----------------------------------------------------------------------------"""
EP_1 = "Unrecognized app_token."
EP_2 = "Post with that title already exists."
EP_3 = "Unknown author. Author must have an admin account."

def EditPost(app_token, post_id, title, author, publication_timestamp, main_image_url, content, tags, category, hidden):
	response = get_default_response()
	try:
		# First authenticate the user and make sure their cookie exists.
		redis_conn = get_redis_conn()
		session = redis_conn.get(app_token)
		if session is None:
			# Unknown g_apptoken.
			# The user is not authenticated.
			response['error_code'] = "EP_1"
			response['error'] = EP_1 
			response = set_response_failed(response)
			return response
		session = json.loads(session)

		pg_conn, pg_curs = get_pg_conn_curser()
		# Insert the post.
		pg_curs.execute("""
		PREPARE CreateNewPost_sub1(text, text, text, text, text, text, boolean, integer) AS
			UPDATE 
				blog_posts
			SET
				title = $1,
				author = $2,
				publication_timestamp = to_timestamp($3, 'dd-mm-yyyy hh24:mi:ss'),
				main_image_url = $4,
				content = $5,
				category = $6,
				hidden = $7
			WHERE
				id = $8;
		EXECUTE CreateNewPost_sub1(%s, %s, %s, %s, %s, %s, %s, %s);
		""",
			(
				title,
				author,
				publication_timestamp,
				main_image_url,
				content,
				category,
				hidden,
				post_id,
			)
		)
		pg_conn.commit()
		pg_conn.close()
		# Delete all the tags associated with the post so you
		# can update them with the one's in this update command.
		pg_conn, pg_curs = get_pg_conn_curser()
		pg_curs.execute("""
		PREPARE CreateNewPost_sub2(text) AS
			DELETE FROM
				blog_post_tags
			WHERE
				post_title = $1;
		EXECUTE CreateNewPost_sub2(%s);
		""",
			(
				title,
			)
		)
		pg_conn.commit()
		pg_conn.close()
		# Associate all the tags.
		# @TODO Figure out what the hell is going on with prepared
		# statements already existing so I don't have to open a new
		# db connection to associate tags.
		for tag in tags:
			pg_conn, pg_curs = get_pg_conn_curser()
			pg_curs.execute("""
			PREPARE CreateNewPost_sub1(text, text) AS
				INSERT INTO
					blog_post_tags
				(
					post_title,
					tag
				) VALUES ($1, $2);
			EXECUTE CreateNewPost_sub1(%s, %s);
			""",
				(
					title,
					tag,
				)
			)
			pg_conn.commit()
			pg_conn.close()
		# Return response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		# Check for foreign key errors.
		if ("title" in str(ex)) and ("already exists" in str(ex)):
			response['error_code'] = "EP_2"
			response['error'] = EP_2
			response = set_response_failed(response)
			return response
		if ("author" in str(ex)) and ("not present" in str(ex)):
			response['error_code'] = "EP_3"
			response['error'] = EP_3
			response = set_response_failed(response)
			return response
		response = set_response_failed(response)
		return response

# print(EditPost("ecqvepmfpwmzzmrqmcbcsvtwqwdrk", 26, "Nexample_title", "example_user@gmail.com", "2017-04-05 21:46:05.243873", "Nexample_main_image_url", "Nexample_content", ["Nexample_tag_1", "Nexapmle_tag_2"], "Nexample_category", False))

"""----------------------------------------------------------------------------
Load Full Post 				(Postgres)
----------------------------------------------------------------------------"""
LFP_1 = "Unknown title."

def LoadFullPost(title):
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
 		# Insert the session into the gitkit_native_message_inbox table.
 		pg_curs.execute("""
 		PREPARE LoadFullPost_sub1(text) AS
			SELECT
				id,
				title,
				author,
				publication_timestamp,
				creation_timestamp,
				main_image_url,
				content,
				category,
				hidden,
				view_count,
				preview_count,
				comment_count
			FROM
				blog_posts
			WHERE
				title = $1;
 		EXECUTE LoadFullPost_sub1(%s);
 		""",
 			(
				title,
 			)
 		)
  		result = pg_curs.fetchone()
 		# If there are no messages, send response back with no empty array.
 		if result is None:
			# Unknown title.
			response['error_code'] = "LFP_1"
			response['error'] = LFP_1 
			response = set_response_failed(response)
			return response

		# Update and increment the post view.
 		pg_curs.execute("""
 		PREPARE LoadFullPost_sub2(text) AS
			UPDATE
				blog_posts
			SET
				view_count = view_count + 1
			WHERE
				title = $1;
 		EXECUTE LoadFullPost_sub2(%s);
 		""",
 			(
				title,
 			)
 		)
		pg_conn.commit()

		# Close the db connection.
		pg_conn.close()

		# Set the respone variables.
		response['id'] = result[0]
		response['title'] = result[1]
		response['author'] = result[2]
		response['publication_timestamp'] = str(result[3])
		response['creation_timestamp'] = str(result[4])
		response['main_image_url'] = result[5]
		response['content'] = result[6]
		response['category'] = result[7]
		response['hidden'] = result[8]
		response['view_count'] = result[9]
		response['preview_count'] = result[10]
		response['comment_count'] = result[11]

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadFullPost("Nexample_title"))

"""----------------------------------------------------------------------------
Load Post Analytics 			(Postgres, Redis)
----------------------------------------------------------------------------"""
def LoadPostAnalytics(cookie, title):
	print("test")
"""----------------------------------------------------------------------------
Load Blog Analytics 			(Postgres, Redis)
----------------------------------------------------------------------------"""
def LoadBlogAnalytics(cookie):
	print("test")
"""----------------------------------------------------------------------------
Load Posts By Category 			(Postgres)
----------------------------------------------------------------------------"""
LPBC_1 = "Unknown category."

def LoadPostsByCategory(category, max_posts, pagination, only_published = True):
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Depending on if the post is published, meaning
		# that the published time is after today, we're going
		# to insert the publish where clause which may be
		# an empty string if the flag 'only_published' is not true.
		if (only_published == True):
			published_where_clause = """
				TO_CHAR(publication_timestamp, 'YYYY-MM-DD') <= TO_CHAR(NOW(), 'YYYY-MM-DD')
			AND
				published = True 
			AND"""
		else:
			published_where_clause = ""
		# Calculate offset from max_posts and pagination.	
		offset = max_posts * pagination
		# You have to concat the sql by yourself if you're
		# going to insert the where clasue because the
		# execute will wrap quote around it thinking it's
		# a string.
		sql = """
 		PREPARE LoadPostsByCategory_sub1(text, integer, integer) AS
			SELECT
				id,
				title,
				author,
				publication_timestamp,
				creation_timestamp,
				main_image_url,
				LEFT(content, 59),
				category,
				hidden,
				view_count,
				preview_count,
				comment_count
			FROM
				blog_posts
			WHERE 
			%s
				category = $1
			ORDER BY 
				publication_timestamp
			DESC
			LIMIT $2
			OFFSET $3;
 		EXECUTE LoadPostsByCategory_sub1('%s', %s, %s);
 		""" % (
			published_where_clause,
			category,
			max_posts,
			offset,
		)
		# Fetch them.
 		pg_curs.execute(sql)
  		result = pg_curs.fetchall()
 		# If there are no posts, send response back with no empty array.
 		if result is None:
			response['posts'] = []
			response = set_response_success(response)
			return response
		posts = []
		post_ids = []
		for row in result:
			post = {}
			post['id'] = row[0]
			post['title'] = row[1]
			post['author'] = row[2]
			post['publication_timestamp'] = str(row[3])
			post['creation_timestamp'] = str(row[4])
			post['main_image_url'] = row[5]
			post['content'] = row[6]
			post['category'] = row[7]
			post['hidden'] = row[8]
			post['view_count'] = row[9]
			post['preview_count'] = row[10]
			post['comment_count'] = row[11]
			posts.append(post)
			post_ids.append(row[0])

		# Update and increment the post view.
		if len(result) != 0:
			update_previews_sql = """
			UPDATE
				blog_posts
			SET
				preview_count = preview_count + 1
			WHERE
				id in (%s)
			""" % (
				','.join(str(post_id) for post_id in post_ids),
			)
			pg_curs.execute(update_previews_sql)
			pg_conn.commit()

		# Close the db connection.
		pg_conn.close()

		response['posts'] = posts

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadPostsByCategory('testthing', 4, 0))
# pp.pprint(LoadPostsByCategory('testthing', 4, 0, False))

"""----------------------------------------------------------------------------
Load Posts By Tag			(Postgres)
----------------------------------------------------------------------------"""
def LoadPostsByTag(tag, max_posts, pagination, only_published = True):
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Depending on if the post is published, meaning
		# that the published time is after today, we're going
		# to insert the publish where clause which may be
		# an empty string if the flag 'only_published' is not true.
		if (only_published == True):
			published_where_clause = """
				TO_CHAR(publication_timestamp, 'YYYY-MM-DD') <= TO_CHAR(NOW(), 'YYYY-MM-DD')
			AND
				published = True 
			AND"""
		else:
			published_where_clause = ""
		# Calculate offset from max_posts and pagination.	
		offset = max_posts * pagination
		# You have to concat the sql by yourself if you're
		# going to insert the where clasue because the
		# execute will wrap quote around it thinking it's
		# a string.
		sql = """
 		PREPARE LoadPostsByTags_sub1(text, integer, integer) AS
			SELECT
				bp.id,
				bp.title,
				bp.author,
				bp.publication_timestamp,
				bp.creation_timestamp,
				bp.main_image_url,
				LEFT(bp.content, 59),
				bp.category,
				bp.hidden,
				bp.view_count,
				bp.preview_count,
				bp.comment_count
			FROM
				blog_posts bp
			LEFT JOIN
				blog_post_tags t
			ON
				bp.title = t.post_title
			WHERE 
			%s
				t.tag = $1
			ORDER BY 
				publication_timestamp
			DESC
			LIMIT $2
			OFFSET $3;
 		EXECUTE LoadPostsByTags_sub1('%s', %s, %s);
 		""" % (
			published_where_clause,
			tag,
			max_posts,
			offset,
		)
		# Fetch them.
 		pg_curs.execute(sql)
  		result = pg_curs.fetchall()
 		# If there are no posts, send response back with no empty array.
 		if result is None:
			response['posts'] = []
			response = set_response_success(response)
			return response
		posts = []
		post_ids = []
		for row in result:
			post = {}
			post['id'] = row[0]
			post['title'] = row[1]
			post['author'] = row[2]
			post['publication_timestamp'] = str(row[3])
			post['creation_timestamp'] = str(row[4])
			post['main_image_url'] = row[5]
			post['content'] = row[6]
			post['category'] = row[7]
			post['hidden'] = row[8]
			post['view_count'] = row[9]
			post['preview_count'] = row[10]
			post['comment_count'] = row[11]
			posts.append(post)
			post_ids.append(row[0])

		# Update and increment the post view.
		if len(result) != 0:
			update_previews_sql = """
			UPDATE
				blog_posts
			SET
				preview_count = preview_count + 1
			WHERE
				id in (%s)
			""" % (
				','.join(str(post_id) for post_id in post_ids),
			)
			pg_curs.execute(update_previews_sql)
			pg_conn.commit()

		# Close the db connection.
		pg_conn.close()

		response['posts'] = posts

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadPostsByTag('Nexample_tag_1', 4, 0))
# pp.pprint(LoadPostsByTag('Nexample_tag_1', 4, 0, False))

"""----------------------------------------------------------------------------
Load Posts Most Recent 			(Postgres)
----------------------------------------------------------------------------"""
def LoadPostsMostRecent(max_posts, pagination, only_published = True):
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Depending on if the post is published, meaning
		# that the published time is after today, we're going
		# to insert the publish where clause which may be
		# an empty string if the flag 'only_published' is not true.
		if (only_published == True):
			published_where_clause = """
			WHERE 
				TO_CHAR(publication_timestamp, 'YYYY-MM-DD') <= TO_CHAR(NOW(), 'YYYY-MM-DD')
			AND
				published = True """
		else:
			published_where_clause = ""
		# Calculate offset from max_posts and pagination.	
		offset = max_posts * pagination
		# You have to concat the sql by yourself if you're
		# going to insert the where clasue because the
		# execute will wrap quote around it thinking it's
		# a string.
		sql = """
 		PREPARE LoadPostsByCategory_sub1(integer, integer) AS
			SELECT
				id,
				title,
				author,
				publication_timestamp,
				creation_timestamp,
				main_image_url,
				LEFT(content, 59),
				category,
				hidden,
				view_count,
				preview_count,
				comment_count
			FROM
				blog_posts
			%s
			ORDER BY 
				publication_timestamp
			DESC
			LIMIT $1
			OFFSET $2;
 		EXECUTE LoadPostsByCategory_sub1(%s, %s);
 		""" % (
			published_where_clause,
			max_posts,
			offset,
		)
		# Fetch them.
 		pg_curs.execute(sql)
  		result = pg_curs.fetchall()
 		# If there are no posts, send response back with no empty array.
 		if result is None:
			response['posts'] = []
			response = set_response_success(response)
			return response
		posts = []
		post_ids = []
		for row in result:
			post = {}
			post['id'] = row[0]
			post['title'] = row[1]
			post['author'] = row[2]
			post['publication_timestamp'] = str(row[3])
			post['creation_timestamp'] = str(row[4])
			post['main_image_url'] = row[5]
			post['content'] = row[6]
			post['category'] = row[7]
			post['hidden'] = row[8]
			post['view_count'] = row[9]
			post['preview_count'] = row[10]
			post['comment_count'] = row[11]
			posts.append(post)
			post_ids.append(row[0])

		# Update and increment the post view.
		if len(result) != 0:
			update_previews_sql = """
			UPDATE
				blog_posts
			SET
				preview_count = preview_count + 1
			WHERE
				id in (%s)
			""" % (
				','.join(str(post_id) for post_id in post_ids),
			)
			pg_curs.execute(update_previews_sql)
			pg_conn.commit()

		# Close the db connection.
		pg_conn.close()

		response['posts'] = posts

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadPostsMostRecent(4, 0))
# pp.pprint(LoadPostsMostRecent(4, 0, False))

"""----------------------------------------------------------------------------
Load Posts Most Viewed			(Postgres)
----------------------------------------------------------------------------"""
def LoadPostsMostViewed(max_posts, pagination, only_published = True):
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Depending on if the post is published, meaning
		# that the published time is after today, we're going
		# to insert the publish where clause which may be
		# an empty string if the flag 'only_published' is not true.
		if (only_published == True):
			published_where_clause = """
			WHERE 
				TO_CHAR(publication_timestamp, 'YYYY-MM-DD') <= TO_CHAR(NOW(), 'YYYY-MM-DD')
			AND
				published = True """
		else:
			published_where_clause = ""
		# Calculate offset from max_posts and pagination.	
		offset = max_posts * pagination
		# You have to concat the sql by yourself if you're
		# going to insert the where clasue because the
		# execute will wrap quote around it thinking it's
		# a string.
		sql = """
 		PREPARE LoadPostsByCategory_sub1(integer, integer) AS
			SELECT
				id,
				title,
				author,
				publication_timestamp,
				creation_timestamp,
				main_image_url,
				LEFT(content, 59),
				category,
				hidden,
				view_count,
				preview_count,
				comment_count
			FROM
				blog_posts
			%s
			ORDER BY 
				view_count
			DESC
			LIMIT $1
			OFFSET $2;
 		EXECUTE LoadPostsByCategory_sub1(%s, %s);
 		""" % (
			published_where_clause,
			max_posts,
			offset,
		)
		# Fetch them.
 		pg_curs.execute(sql)
  		result = pg_curs.fetchall()
 		# If there are no posts, send response back with no empty array.
 		if result is None:
			response['posts'] = []
			response = set_response_success(response)
			return response
		posts = []
		post_ids = []
		for row in result:
			post = {}
			post['id'] = row[0]
			post['title'] = row[1]
			post['author'] = row[2]
			post['publication_timestamp'] = str(row[3])
			post['creation_timestamp'] = str(row[4])
			post['main_image_url'] = row[5]
			post['content'] = row[6]
			post['category'] = row[7]
			post['hidden'] = row[8]
			post['view_count'] = row[9]
			post['preview_count'] = row[10]
			post['comment_count'] = row[11]
			posts.append(post)
			post_ids.append(row[0])

		# Update and increment the post view.
		if len(result) != 0:
			update_previews_sql = """
			UPDATE
				blog_posts
			SET
				preview_count = preview_count + 1
			WHERE
				id in (%s)
			""" % (
				','.join(str(post_id) for post_id in post_ids),
			)
			pg_curs.execute(update_previews_sql)
			pg_conn.commit()

		# Close the db connection.
		pg_conn.close()

		response['posts'] = posts

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadPostsMostViewed(4, 0))
# pp.pprint(LoadPostsMostViewed(4, 0, False))

"""----------------------------------------------------------------------------
Load Posts Most Previewed		(Postgres)
----------------------------------------------------------------------------"""
def LoadPostsMostPreviewed(max_posts, pagination, only_published = True):
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Depending on if the post is published, meaning
		# that the published time is after today, we're going
		# to insert the publish where clause which may be
		# an empty string if the flag 'only_published' is not true.
		if (only_published == True):
			published_where_clause = """
			WHERE 
				TO_CHAR(publication_timestamp, 'YYYY-MM-DD') <= TO_CHAR(NOW(), 'YYYY-MM-DD')
			AND
				published = True """
		else:
			published_where_clause = ""
		# Calculate offset from max_posts and pagination.	
		offset = max_posts * pagination
		# You have to concat the sql by yourself if you're
		# going to insert the where clasue because the
		# execute will wrap quote around it thinking it's
		# a string.
		sql = """
 		PREPARE LoadPostsByCategory_sub1(integer, integer) AS
			SELECT
				id,
				title,
				author,
				publication_timestamp,
				creation_timestamp,
				main_image_url,
				LEFT(content, 59),
				category,
				hidden,
				view_count,
				preview_count,
				comment_count
			FROM
				blog_posts
			%s
			ORDER BY 
				preview_count
			DESC
			LIMIT $1
			OFFSET $2;
 		EXECUTE LoadPostsByCategory_sub1(%s, %s);
 		""" % (
			published_where_clause,
			max_posts,
			offset,
		)
		# Fetch them.
 		pg_curs.execute(sql)
  		result = pg_curs.fetchall()
 		# If there are no posts, send response back with no empty array.
 		if result is None:
			response['posts'] = []
			response = set_response_success(response)
			return response
		posts = []
		post_ids = []
		for row in result:
			post = {}
			post['id'] = row[0]
			post['title'] = row[1]
			post['author'] = row[2]
			post['publication_timestamp'] = str(row[3])
			post['creation_timestamp'] = str(row[4])
			post['main_image_url'] = row[5]
			post['content'] = row[6]
			post['category'] = row[7]
			post['hidden'] = row[8]
			post['view_count'] = row[9]
			post['preview_count'] = row[10]
			post['comment_count'] = row[11]
			posts.append(post)
			post_ids.append(row[0])

		# Update and increment the post view.
		if len(result) != 0:
			update_previews_sql = """
			UPDATE
				blog_posts
			SET
				preview_count = preview_count + 1
			WHERE
				id in (%s)
			""" % (
				','.join(str(post_id) for post_id in post_ids),
			)
			pg_curs.execute(update_previews_sql)
			pg_conn.commit()

		# Close the db connection.
		pg_conn.close()

		response['posts'] = posts

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadPostsMostPreviewed(4, 0))
# pp.pprint(LoadPostsMostPreviewed(4, 0, False))

"""----------------------------------------------------------------------------
Load All Categories 			(Postgres)
----------------------------------------------------------------------------"""
def LoadAllCategories():
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Fetch them.
 		pg_curs.execute("""
		SELECT DISTINCT
			category,
			COUNT(*)
		FROM
			blog_posts
		GROUP BY 1
		""")
  		result = pg_curs.fetchall()
 		# If there are no categories, send response back with no empty array.
 		if result is None:
			response['categories'] = []
			response = set_response_success(response)
			return response
		categories = []
		for row in result:
			category = {}
			category['name'] = row[0]
			category['count'] = row[1]
			categories.append(category)
		pg_conn.close()
		response['categories'] = categories 

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadAllCategories())

"""----------------------------------------------------------------------------
Load All Tags 				(Postgres)
----------------------------------------------------------------------------"""
def LoadAllTags():
	response = get_default_response()
	try:
 		pg_conn, pg_curs = get_pg_conn_curser()
		# Fetch them.
 		pg_curs.execute("""
		SELECT DISTINCT
			tag,
			COUNT(*)
		FROM
			blog_post_tags
		GROUP BY 1
		""")
  		result = pg_curs.fetchall()
 		# If there are no tags, send response back with no empty array.
 		if result is None:
			response['tags'] = []
			response = set_response_success(response)
			return response
		tags = []
		for row in result:
			tag = {}
			tag['name'] = row[0]
			tag['count'] = row[1]
			tags.append(tag)
		pg_conn.close()
		response['tags'] = tags

		# Return the response.
		response = set_response_success(response)
		return response
	except Exception as ex:
		log_auth_exception(ex)
		# Close the db connection.
		try:
			pg_conn.close()
		except:
			pass
		# Return default failure response.
		response = set_response_failed(response)
		return response

# import pprint as pp
# pp.pprint(LoadAllTags())
