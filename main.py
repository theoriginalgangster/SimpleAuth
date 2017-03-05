# sample.py
import falcon
import json
import core
 
class QuoteResource:
    def on_post(self, req, resp):
        """Handles GET requests"""
	api_resp = {
		"success": "false",
		"error": "Invalid API Request.",
		"error_code": "API_1"
	}

	try:
		core_req = json.loads(req.stream.read().encode("utf-8"))
		import pprint as pp
		pp.pprint(core_req)
		if core_req["command"] == "log_in":
			core_resp = core.LogUserIn(
				core_req["user_name"], 
				core_req["password"].encode("utf-8"))
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "log_out":
			core_resp = core.LogUserOut(core_req["cookie"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "register_user":
			core_resp = core.RegisterUser(core_req["user_name"], core_req["password"].encode("utf-8"))
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "unregister_user":
			core_resp = core.UnregisterUser(core_req["user_name"], core_req["cookie"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "read_session_vars":
			core_resp = core.ReadSessionVars(core_req["cookie"], core_req["session_keys"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "set_session_vars":
			core_resp = core.SetSessionVars(core_req["cookie"], core_req["session_vars"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "unset_session_vars":
			core_resp = core.UnsetSessionVars(core_req["cookie"], core_req["session_keys"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "register_role":
			core_resp = core.RegisterRole(core_req["admin_key"], core_req["role_name"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "unregister_role":
			core_resp = core.UnregisterRole(core_req["admin_key"], core_req["role_name"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "associate_user_role":
			core_resp = core.AssociateUserRole(core_req["admin_key"], core_req["user_name"], core_req["role_name"])
        		resp.body = json.dumps(core_resp)
		elif core_req["command"] == "disassociate_user_role":
			core_resp = core.DisassociateUserRole(core_req["admin_key"], core_req["user_name"], core_req["role_name"])
        		resp.body = json.dumps(core_resp)
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
