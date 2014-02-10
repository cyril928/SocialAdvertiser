# Python
import urllib, simplejson
import ast
import subprocess
import pycurl
# Custom
from app_auth.models import FacebookUser

#get user's profile
def get_facebook_profile(user):
   
    try:
        fb_user = FacebookUser.objects.get(user=user)
        user_json = urllib.urlopen('https://graph.facebook.com/me?'  + urllib.urlencode(dict(access_token=fb_user.access_token)))
        profile = simplejson.load(user_json)
        return profile
    except:
        return None

#get user's like_page
def get_facebook_likes(user):
	
	try:
		fb_user = FacebookUser.objects.get(user=user)
		likes_json = urllib.urlopen('https://graph.facebook.com/me/likes?' + urllib.urlencode(dict(access_token=fb_user.access_token)))
		likes = simplejson.load(likes_json)
		return likes
	except:
		return None

#get user's friends
def get_facebook_friends(user):
		
	try:
		fb_user = FacebookUser.objects.get(user=user)
		friends_json = urllib.urlopen('https://graph.facebook.com/me/friends?' + urllib.urlencode(dict(access_token=fb_user.access_token)))
		friends = simplejson.load(friends_json)
		return friends
	except:
		return None

#get user's friends' like_page
def get_facebook_friends_likes(user,friendID):

	try: 
		fb_user = FacebookUser.objects.get(user=user)			
		friend_likes_json = urllib.urlopen('https://graph.facebook.com/%s/likes?' % (friendID) + urllib.urlencode(dict(access_token=fb_user.access_token)))
		friend_likes = simplejson.load(friend_likes_json)
		return friend_likes
	except:
		return None

#get user's like_page and friend in a batch way
def batch_get_facebook(user):
        		
	#batch_request = '[{"method":"GET","relative_url":"me/likes"},'+'{"method":"GET","name":"get-friends","omit_response_on_success":false,"relative_url":"me/friends"},'+'{"method":"GET","relative_url":"{result=get-friends:$.data.0.id}/likes"}]'
	batch_request = '[{"method":"GET","relative_url":"me/likes"},'+'{"method":"GET","relative_url":"me/friends"}]'

	try:
		fb_user = FacebookUser.objects.get(user=user)			
			
		args = {
			'access_token':fb_user.access_token,
			'batch':batch_request,
			'method':'POST',
		}
		
		#batch_response_array is a json array		
		batch_response_array = urllib.urlopen('https://graph.facebook.com/?' + urllib.urlencode(args))
		
		batch_response_json = simplejson.load(batch_response_array)	
		#print ('https://graph.facebook.com/?' + urllib.urlencode(args))
		batch_json = []
		for batch_response in batch_response_json:
			batch_json.append(batch_response['body'])
		return batch_json
			
	except:
		return None

def batch_get_friend_likes(user,friend_list,batch_index):
	
	#more efficient way to build long string
	if len(friend_list)-batch_index < 20:
		batch_num = len(friend_list)-batch_index 
	else:
		batch_num = 20
	
	buf = ['[']	
	for i in range(batch_index,batch_index+batch_num):		
		buf.append('{"method":"GET","relative_url":"')
		buf.append(friend_list[i])	
		buf.append('/likes"},')
	buf.append(']')
	
	#print len(friend_list)	
	batch_request = ''.join(buf)
	try:
		fb_user = FacebookUser.objects.get(user=user)			
			
		args = {
			'access_token':fb_user.access_token,
			'batch':batch_request,
			'method':'POST',
		}
				
		batch_response_array = urllib.urlopen('https://graph.facebook.com/?' + urllib.urlencode(args))
		batch_response_json = simplejson.load(batch_response_array)	
		
		#print ('https://graph.facebook.com/?' + urllib.urlencode(args))
		batch_json = []
		for batch_response in batch_response_json:
			batch_json.append(batch_response['body'])
		return batch_json
			
	except:
		return None
		
def write_Mapfile(user):
		
		user_profile = get_facebook_profile(user)
		user_likes = get_facebook_likes(user)
		
		if len(user_likes) > 0:  		
			f = open('./facebook_graph/{0}'.format(user_profile['id']), 'w')
			for like_page in user_likes['data']:
				f.write('{0},{1}\n'.format(user_profile['id'],like_page['category']).lower())
				
		user_friends = get_facebook_friends(user)		
		for friend in user_friends['data']:
			friend_likes = get_facebook_friends_likes(user, friend['id'])
			for like_page in friend_likes['data']:
				f.write('{0}:friend,{1}\n'.format(user_profile['id'],like_page['category']).lower())

		f.close()

def batch_write_Mapfile(user):
		
		user_profile = get_facebook_profile(user)
		batch_result = batch_get_facebook(user)

		f = open('./facebook_graph/{0}'.format(user_profile['id']), 'w')

		try : 
			
			#because it has been put in list previously, it converts from json obj to string
			#now we should convert json str to dictionary 
			dic_batch = ast.literal_eval(batch_result[0])
			
			for like_page in dic_batch['data']:
				f.write('{0},{1}\n'.format(user_profile['id'],like_page['category'].replace('\\','')).lower())
		except KeyError:	
			print "batch request personal like is failed"
			
		try:			

			#because it has been put in list previously, it converts from json obj to string
			#now we should convert json str to dictionary 			
			dic_batch = ast.literal_eval(batch_result[1])

			friend_list = []
			for friend in dic_batch['data']:
				friend_list.append(friend['id'])
			
			batch_friend_likes_result = []
			for batch_index in range(0,len(friend_list),20):
				batch_friend_likes_result = batch_get_friend_likes(user,friend_list, batch_index)
			
				#print(len(batch_friend_likes_result))	
				for i in range(0,len(batch_friend_likes_result)):
					dic_batch = ast.literal_eval(batch_friend_likes_result[i])
					
					try:
						for friend_like_page in dic_batch['data']:
							f.write('{0}:friend,{1}\n'.format(user_profile['id'],friend_like_page['category'].replace('\\','')).lower())

					except KeyError:
						print "batch request friends' like is failed"

						
		except KeyError:
			print "batch request personal friends is failed"
	
		print "writing file %s is finished" % user_profile['id'] 
		f.close()
