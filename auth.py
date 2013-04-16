import sys
if 'lib' not in sys.path:
  sys.path[0:0] = ['lib']

import webapp2
import logging
from webapp2_extras import routes

import request
from secrets import HOST, AUTH_CONFIG
from simpleauth import SimpleAuthHandler

class AuthHDL(request.RequestHandler, SimpleAuthHandler):
  """Authentication handler for OAuth 2.0, 1.0(a) and OpenID."""

  # Enable optional OAuth 2.0 CSRF guard
  OAUTH2_CSRF_STATE = True
  
  USER_ATTRS = {
    'facebook' : {
      'id'     : lambda id: ('avatar_url', 
        'http://graph.facebook.com/{0}/picture?type=large'.format(id)),
      'name'   : 'name',
      'link'   : 'link'
    },
    'google'   : {
      'picture': 'avatar_url',
      'name'   : 'name',
      'link'   : 'link'
    }
    ,
    'windows_live': {
      'avatar_url': 'avatar_url',
      'name'      : 'name',
      'link'      : 'link'
    },
    'twitter'  : {
      'profile_image_url': 'avatar_url',
      'screen_name'      : 'name',
      'link'             : 'link'
    },
    'linkedin' : {
      'picture-url'       : 'avatar_url',
      'first-name'        : 'name',
      'public-profile-url': 'link'
    },
    'foursquare'   : {
      'photo'    : lambda photo: ('avatar_url', photo.get('prefix') + '100x100' + photo.get('suffix')),
      'firstName': 'firstName',
      'lastName' : 'lastName',
      'contact'  : lambda contact: ('email',contact.get('email')),
      'id'       : lambda id: ('link', 'http://foursquare.com/user/{0}'.format(id))
    },
    'openid'   : {
      'id'      : lambda id: ('avatar_url', '/img/missing-avatar.png'),
      'nickname': 'name',
      'email'   : 'link'
    }
  }
  
  def _on_signin(self, data, auth_info, provider):
    """Callback whenever a new or existing user is logging in.
     data is a user info dictionary.
     auth_info contains access token or oauth token and secret.
    """
    auth_id = '%s:%s' % (provider, data['id'])
    logging.info('Looking for a user with id %s', auth_id)
    
    user = self.auth.store.user_model.get_by_auth_id(auth_id)
    _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])

    logging.info(_attrs)

    if user:
      logging.info('Found existing user to log in')
      # Existing users might've changed their profile data so we update our
      # local model anyway. This might result in quite inefficient usage
      # of the Datastore, but we do this anyway for demo purposes.
      #
      # In a real app you could compare _attrs with user's properties fetched
      # from the datastore and update local user in case something's changed.
      user.populate(**_attrs)
      user.put()
      self.auth.set_session(
        self.auth.store.user_to_dict(user))
      
    else:
      # check whether there's a user currently logged in
      # then, create a new user if nobody's signed in, 
      # otherwise add this auth_id to currently logged in user.

      if self.logged_in:
        logging.info('Updating currently logged in user')
        
        u = self.current_user
        u.populate(**_attrs)
        # The following will also do u.put(). Though, in a real app
        # you might want to check the result, which is
        # (boolean, info) tuple where boolean == True indicates success
        # See webapp2_extras.appengine.auth.models.User for details.
        u.add_auth_id(auth_id)
        
      else:
        logging.info('Creating a brand new user')
        _attrs['pub_id'] = ''
        ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
        if ok:
          self.auth.set_session(self.auth.store.user_to_dict(user))

    active = False
    try:
      active = user.active
    except AttributeError:
      pass

    if not active:
      self.auth.unset_session()
      self.redirect('/beta')
      return

    self.redirect('/settings')

  def logout(self):
    self.auth.unset_session()
    self.redirect('/')

  def handle_exception(self, exception, debug):
    logging.error(exception)
    """
    self.render('error.html', {'exception': exception})
    """
    self.redirect('/')
    
  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)
    
  def _get_consumer_info_for(self, provider):
    """Returns a tuple (key, secret) for auth init requests."""
    return AUTH_CONFIG[provider]
    
  def _to_user_model_attrs(self, data, attrs_map):
    """Get the needed information from the provider dataset."""
    user_attrs = {}
    for k, v in attrs_map.iteritems():
      attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
      user_attrs.setdefault(*attr)

    return user_attrs

app = webapp2.WSGIApplication([
  routes.DomainRoute('<:(www.%s|localhost)>'%HOST, [
    webapp2.Route('/logout', handler='auth.AuthHDL:logout', name='logout'),
    webapp2.Route('/auth/<provider>', handler='auth.AuthHDL:_simple_auth', name='auth_login'),
    webapp2.Route('/auth/<provider>/callback', handler='auth.AuthHDL:_auth_callback', name='auth_callback')
  ])
], debug=True, config=request.app_config)
