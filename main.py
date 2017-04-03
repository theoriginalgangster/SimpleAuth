import falcon
import json
import auth
 
class QuoteResource:
    def on_post(self, req, resp):
        """Handles GET requests"""
	api_resp = {
		"success": "false",
		"error": "Invalid API Request.",
		"error_code": "API_1"
	}

	try:
		auth_req = json.loads(req.stream.read().encode("utf-8"))
		if auth_req["command"] == "log_in":
			auth_resp = auth.LogUserIn(auth_req["user_name"], auth_req["password"].encode("utf-8"))
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "log_out":
			auth_resp = auth.LogUserOut(auth_req["cookie"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "register_user":
			auth_resp = auth.RegisterUser(auth_req["user_name"], auth_req["password"].encode("utf-8"))
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "unregister_user":
			auth_resp = auth.UnregisterUser(auth_req["user_name"], auth_req["cookie"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "read_session_vars":
			auth_resp = auth.ReadSessionVars(auth_req["cookie"], auth_req["session_keys"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "set_session_vars":
			auth_resp = auth.SetSessionVars(auth_req["cookie"], auth_req["session_vars"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "unset_session_vars":
			auth_resp = auth.UnsetSessionVars(auth_req["cookie"], auth_req["session_keys"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "register_role":
			auth_resp = auth.RegisterRole(auth_req["admin_key"], auth_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "unregister_role":
			auth_resp = auth.UnregisterRole(auth_req["admin_key"], auth_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "associate_user_role":
			auth_resp = auth.AssociateUserRole(auth_req["admin_key"], auth_req["user_name"], auth_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		elif auth_req["command"] == "disassociate_user_role":
			auth_resp = auth.DisassociateUserRole(auth_req["admin_key"], auth_req["user_name"], auth_req["role_name"])
        		resp.body = json.dumps(auth_resp)
		else:
			api_resp["error"] = "Unrecognized Command."
			api_resp["error_code"] = "API_2"
        		resp.body = json.dumps(api_resp)
	except Exception as ex:
		print(ex)
		print("THING")
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
