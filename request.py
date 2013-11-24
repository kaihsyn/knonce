import webapp2
import logging
import json
from webapp2_extras import auth, sessions, jinja2
from jinja2.runtime import TemplateNotFound
from secrets import SESSION_KEY

# webapp2 config
app_config = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': SESSION_KEY
    },
    'webapp2_extras.auth': {
        'user_attributes': []
    }
}

# Session Handling class, gets the store, dispatches the request
class RequestHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property    
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def current_user(self):
        """Returns currently logged in user"""
        user_dict = self.auth.get_user_by_session()
        return self.auth.store.user_model.get_by_id(user_dict['user_id'])
      
    @webapp2.cached_property
    def logged_in(self):
        """Returns true if a user is currently logged in, false otherwise"""
        return self.auth.get_user_by_session() is not None and self.current_user.active

    def render(self, template_name, template_vars={}):
        # Preset values for the template
        values = {
            'logged_in': self.logged_in,
            'flashes': self.session.get_flashes()
        }
    
        # Add manually supplied template values
        values.update(template_vars)
        
        # read the template or 404.html
        try:
            self.response.write(self.jinja2.render_template(template_name, **values))
        except TemplateNotFound:
            logging.info(jinja2.default_config)
            self.abort(404)

    def render_json(self, json_vars={}):
        self.response.headers['Content-Type'] = 'application/json'
        return self.response.out.write(json.dumps(json_vars))
  