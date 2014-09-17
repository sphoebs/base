#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import logging
import config
from google.appengine.ext import ndb


import sys
sys.path.append('flib/')
sys.path.append('data/')

import social_login
from social_login import LoginManager
from GFuser import GFUser

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    #extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class PUSer(GFUser):
    someOtherPar = ndb.StringProperty()

def get_current_user(request, cookie_name):
        user_id = social_login.parse_cookie(request.cookies.get(cookie_name), config.LOGIN_COOKIE_DURATION)
        
        if user_id:
            logging.error("\n USER ID COOKIE DETECTED \n")
            logging.error('::get_current_user:: returning user' + user_id)
            user = PUser.query(PUser.user_id==user_id).get() 
            logging.error('\n ::user object:: returning user' + str(user))
            return PUser.get_by_user_id(user_id) 

        
        
class BaseRequestHandler(webapp2.RequestHandler):
    
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)



    def render(self, template_name, template_vars={}):
     values={}
     values.update(template_vars)
     try:
       template=JINJA_ENVIRONMENT.get_template(template_name)
       self.write(template.render(**values))
     except:
       logging.error("Rendering Exception for " + template_name)
       self.abort(404)



    def dispatch(self):  
        self.pars={}
        user = get_current_user(self.request, 'user_id')
        self.pars.update({'user': user})
        #get user
        
        logging.error("\n self.pars" + str (self.pars))
        webapp2.RequestHandler.dispatch(self)
        
        
class LoginHandler(BaseRequestHandler):
    def get(self):
        
        if '/fb/oauth_callback' in self.request.url:
            logging.error("\n \n FB request: "+str(self.request.url))
            
            oauth_user_dictionary, access_token, errors = LoginManager.handle_oauth_callback(self.request, 'facebook')
            
            user, result = PUser.add_or_get_user(oauth_user_dictionary, access_token, 'facebook')

            
        elif '/google/oauth_callback' in self.request.url:
            oauth_user_dictionary, access_token, errors = LoginManager.handle_oauth_callback(self.request, 'google')
            
            user, result = PUser.add_or_get_user(oauth_user_dictionary, access_token, 'google')
            #set cookie
            #redirect
            pass
        else:
            logging.error('illegal callback invocation')
        
        
        BaseHandler.set_cookie(self.response, "user", str(user.user_id), expires=time.time() + settings.LOGIN_COOKIE_DURATION, encrypt=True)
        self.redirect('/') 


class MainHandler(BaseRequestHandler):
    def get(self):
         
        login_urls = LoginManager.get_login_URLs(self.request)
        
        self.render('landing.html', login_urls)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/fb/oauth_callback/?',LoginHandler),
    ('/google/oauth_callback/?',LoginHandler)
], debug=True)
