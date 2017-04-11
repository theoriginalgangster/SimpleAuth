import falcon
import json
import auth
import messaging
import blogging

class QuoteResource:
    def on_post(self, req, resp):
        """Handles GET requests"""
	api_resp = {
		"success": "false",
		"error": "Invalid API Request.",
		"error_code": "API_1"
	}

	try:
		api_req = json.loads(req.stream.read().encode("utf-8"))
		# All auth module commands.
		if api_req["command"] == "log_in":
			auth_resp = auth.LogUserIn(api_req["user_name"], api_req["password"].encode("utf-8"))
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "log_out":
			auth_resp = auth.LogUserOut(api_req["cookie"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "force_log_out":
			auth_resp = auth.ForceLogUserOut(api_req["user_name"], api_req["admin_key"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "register_user":
			auth_resp = auth.RegisterUser(api_req["user_name"], api_req["password"].encode("utf-8"))
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "unregister_user":
			auth_resp = auth.UnregisterUser(api_req["user_name"], api_req["cookie"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "read_session_vars":
			auth_resp = auth.ReadSessionVars(api_req["cookie"], api_req["session_keys"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "set_session_vars":
			auth_resp = auth.SetSessionVars(api_req["cookie"], api_req["session_vars"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "unset_session_vars":
			auth_resp = auth.UnsetSessionVars(api_req["cookie"], api_req["session_keys"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "register_role":
			auth_resp = auth.RegisterRole(api_req["admin_key"], api_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "unregister_role":
			auth_resp = auth.UnregisterRole(api_req["admin_key"], api_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "associate_user_role":
			auth_resp = auth.AssociateUserRole(api_req["admin_key"], api_req["user_name"], api_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "disassociate_user_role":
			auth_resp = auth.DisassociateUserRole(api_req["admin_key"], api_req["user_name"], api_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "handle_only_gitkit_token":
			auth_resp = auth.HandleOnlyGitkitToken(api_req["email_address"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "read_gitkit_user_session_vars":
			auth_resp = auth.ReadGitkitUserSessionVars(api_req["g_apptoken"], api_req["session_keys"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "gitkit_user_log_out":
			auth_resp = auth.GitkitUserLogOut(api_req["g_apptoken"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "force_gitkit_user_log_out":
			auth_resp = auth.ForceGitkitUserLogOut(api_req["email_address"], api_req["admin_key"])
        		resp.body = json.dumps(auth_resp)
		elif api_req["command"] == "confirm_user_role":
			auth_resp = auth.ConfirmUserRole(api_req["cookie"], api_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		# All messaging module commands.
		elif api_req["command"] == "g_send_message":
			messaging_resp = messaging.GSendMessage(api_req["g_apptoken"], api_req["recipient"], api_req["message"])
        		resp.body = json.dumps(messaging_resp)
		elif api_req["command"] == "g_read_messages":
			messaging_resp = messaging.GReadMessages(api_req["g_apptoken"], api_req["chat_partner"], api_req["max_messages"])
        		resp.body = json.dumps(messaging_resp)
		elif api_req["command"] == "send_message":
			messaging_resp = messaging.SendMessage(api_req["apptoken"], api_req["recipient"], api_req["message"])
        		resp.body = json.dumps(messaging_resp)
		elif api_req["command"] == "read_messages":
			messaging_resp = messaging.ReadMessages(api_req["apptoken"], api_req["chat_partner"], api_req["max_messages"])
        		resp.body = json.dumps(messaging_resp)
		# All blogging module commands.
		elif api_req["command"] == "create_new_post":
			blogging_resp = blogging.CreateNewPost(api_req['app_token'],api_req['title'],api_req['author'],api_req['publication_timestamp'],api_req['main_image_url'],api_req['content'],api_req['tags'],api_req['category'],api_req['hidden'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "edit_post":
			blogging_resp = blogging.EditPost(api_req['app_token'],api_req['post_id'],api_req['title'],api_req['author'],api_req['publication_timestamp'],api_req['main_image_url'],api_req['content'],api_req['tags'],api_req['category'],api_req['hidden'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_full_post":
			blogging_resp = blogging.LoadFullPost(api_req['title'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_posts_by_category":
			print("OK")
			import pprint as pp
			pp.pprint(api_req)
			blogging_resp = blogging.LoadPostsByCategory(api_req['category'],api_req['max_posts'],api_req['pagination'],api_req['only_published'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_posts_by_tag":
			blogging_resp = blogging.LoadPostsByTag(api_req['tag'],api_req['max_posts'],api_req['pagination'],api_req['only_published'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_posts_most_recent":
			blogging_resp = blogging.LoadPostsMostRecent(api_req['max_posts'],api_req['pagination'],api_req['only_published'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_posts_most_viewed":
			blogging_resp = blogging.LoadPostsMostViewed(api_req['max_posts'],api_req['pagination'],api_req['only_published'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_posts_most_previewed":
			blogging_resp = blogging.LoadPostsMostPreviewed(api_req['max_posts'],api_req['pagination'],api_req['only_published'])
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_all_categories":
			blogging_resp = blogging.LoadAllCategories()
        		resp.body = json.dumps(blogging_resp)
		elif api_req["command"] == "load_all_tags":
			blogging_resp = blogging.LoadAllTags()
        		resp.body = json.dumps(blogging_resp)
		else:
			api_resp["error"] = "Unrecognized Command."
			api_resp["error_code"] = "API_2"
        		resp.body = json.dumps(api_resp)
	except Exception as ex:
		print("ex: ")
		print(ex)
		resp.body = json.dumps(api_resp)


class AdminResource:
	def on_get(self, req, resp):
		resp.status = falcon.HTTP_200
		resp.content_type = "text/html"
		with open("admin.html", "r") as f:
			resp.body = f.read()
 
api = falcon.API()
api.add_route('/api', QuoteResource())
api.add_route('/admin', AdminResource())
