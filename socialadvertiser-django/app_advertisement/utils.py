# Python
import urllib, simplejson
import ast
import subprocess
import pycurl
# Custom
from app_auth.models import FacebookUser

def publish_ad(user,message):

	try:
		fb_user = FacebookUser.objects.get(user=user)			
			
		args = {
			'access_token':fb_user.access_token,
			'message':message,
			'method':'POST'
		}
				
		print 'https://graph.facebook.com/'+ fb_user.facebook_id + '/feed?' + urllib.urlencode(args)
		batch_response_array = urllib.urlopen('https://graph.facebook.com/'+ fb_user.facebook_id + '/feed?' + urllib.urlencode(args))

		batch_response_json = simplejson.load(batch_response_array)
		return batch_response_json
	except:
		return None

