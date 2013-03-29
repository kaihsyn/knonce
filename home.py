import logging
import webapp2
import jinja2
import os

class MainHandler(webapp2.RequestHandler):
	def get(self):

		template = jinja_environment.get_template('views/home.html')
		self.response.out.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))