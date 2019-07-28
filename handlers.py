import logging
import json

import webapp2
import os
from google.appengine.api import users
from google.appengine.ext.webapp import template
from method import Analyzer



class MainPage(webapp2.RequestHandler):
	"""return main page"""
	def get(self):
		
		if users.get_current_user():
			template_values = {
				'UserName': users.get_current_user()
			}

		path = os.path.join(os.path.dirname(__file__), 'app/index.html')
		self.response.out.write(template.render(path, template_values))

#handler to get uploaded sms backup
#return 
class SMSBackUp(webapp2.RequestHandler):
	"""get the user sms backup and analyze it""" 
	def post(self):
		try:
			smsBackUp = json.loads(self.request.get('file'))
			analyze = Analyzer(smsBackUp)
			template_values = {
				'UserName': users.get_current_user(),
				'results':analyze.find()
			}
			path = os.path.join(os.path.dirname(__file__), 'app/index.html')
			self.response.out.write(template.render(path, template_values))
		except ValueError:
			self.redirect('/')
		