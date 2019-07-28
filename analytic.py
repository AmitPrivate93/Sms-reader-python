import os
import cgi
import webapp2
from handlers import MainPage,SMSBackUp



app = webapp2.WSGIApplication([
	('/', MainPage),
	('/upload',SMSBackUp)
], debug=True)


# re.findall(rgx,str)
# dt = datetime.strptime("2016-05-04:20:03:28", "%Y-%m-%d:%H:%M:%S")
# dt.strftime('%d-%B-%Y %I:%M %p')
# '04-May-2016 08:03 PM'