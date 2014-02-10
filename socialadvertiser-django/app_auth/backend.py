# Python
import urllib, cgi, simplejson

# Django
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

# Custom
from app_auth.models import *
from app_auth.utils import *

THIS_YEAR = 2011

class FacebookBackend:
	def authenticate(self, token=None, request=None):
		args = {
						'client_id': settings.FACEBOOK_APP_ID,
						'client_secret': settings.FACEBOOK_APP_SECRET,
						'redirect_uri': request.build_absolute_uri('/auth/facebook/'),
						'code': token,
		}		
		target = urllib.urlopen('https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)).read()
		response = cgi.parse_qs(target)
		access_token = response['access_token'][-1]
		user_json = urllib.urlopen('https://graph.facebook.com/me?' + urllib.urlencode(dict(access_token=access_token)))
		fb_profile = simplejson.load(user_json)

		try:
			fb_user = FacebookUser.objects.get(facebook_id=fb_profile['id'])
		except FacebookUser.DoesNotExist:          
			fb_user = FacebookUser(user=request.user, facebook_id=fb_profile['id'])

		fb_user.access_token = access_token

		friends_json = urllib.urlopen('https://graph.facebook.com/me/friends?' + urllib.urlencode(dict(access_token=fb_user.access_token)))
		friends = simplejson.load(friends_json)

		fb_user.contacts = len(friends['data'])		
		try:
			birthday = fb_profile['birthday'].split('/')
		except KeyError:
			pass    
		age = THIS_YEAR - int(birthday[2])			

		try:
			fb_user.gender = fb_profile['gender']
		except KeyError:
			pass
		try:
			fb_user.location = fb_profile['location']['name']
		except KeyError:
			pass
		fb_user.age = age
		fb_user.save()

		return fb_user.user

	supports_object_permissions = False
	supports_anonymous_user = False
