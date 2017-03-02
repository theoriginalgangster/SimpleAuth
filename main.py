# sample.py
import falcon
import json
import core
 
class QuoteResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # quote = {
        #     'quote': 'I\'ve always been more interested in the future than in the past.',
        #     'author': 'Grace Hopper'
        # }
	
	####################
	# UNCOMMENT FOR TESTING WITH CORE INFLUENCED SPEED
	####################
	# quote = ReadSessionVariables('hmpnorcjnlzqsppnmwoymnrerheqq', ['creation_timestamp', 'cookie', 'asdfasdf'])

	####################
	# UNCOMMENT FOR TESTING WITHOUT CORE INFLUENCED SPEED
	####################
        resp.body = json.dumps("wazzup")
 
api = falcon.API()
api.add_route('/quote', QuoteResource())
