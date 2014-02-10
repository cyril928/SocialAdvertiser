import urlparse
import twitter
import oauth2 as oauth
import urllib, simplejson
import thread

try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from app_content.models import *
from app_auth.models import *
from app_auth.forms import *
from app_advertisement.models import *

from app_auth.utils import *


# Global constants
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'

consumer_key = getattr(settings, 'CONSUMER_KEY', None)
consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)

client = None
consumer = None


@csrf_protect
def signup(request):
    context = RequestContext(request)
    form = SigninForm()
    
    if request.method == 'POST':
        signup_form = SignupForm(data=request.POST)
        if signup_form.is_valid():
            new_profile = signup_form.save()
            return render_to_response('auth/signup_successful.html', locals())
    else:
        signup_form = SignupForm()
    
    return render_to_response('auth/signup_form.html', 
        { 'signup_form': signup_form, 'form': form }, 
        context_instance=context)
    
    
def activate(request, key):
    profile_activated = UserProfile.objects.activate_user(activation_key=key)
    form = SigninForm()
    
    if profile_activated is not None:
        return render_to_response('auth/activation_successful.html', locals())
    else:
        return render_to_response('auth/activation_error.html', locals())
    

@csrf_protect
def signin(request, redirect_on_success='/profile/'):
    context = RequestContext(request)
    
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = User.objects.get(username=username)
            user_cache = authenticate(username=username, password=password)
            if user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))
            login(request, user_cache)
            return HttpResponseRedirect(redirect_on_success)
    else:
        form = SigninForm()
        
    return HttpResponseRedirect('/')

    
def signout(request, redirect_on_success="/"):
    logout(request)
    return HttpResponseRedirect(redirect_on_success)
    
    
def profile(request):
	
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/signin/')

	user = request.user
	profile = UserProfile.objects.get(user=user)
	if profile.role == 'merchant':
		try:
			ads = Advertisement.objects.filter(merchant=profile)
		except Advertisement.DoesNotExist:
			pass
		
	else:
		if profile.twitter_activated == True:
			try:
				twitter_ads = Advertisement.objects.filter(advertisers__in=[profile])
			except Advertisement.DoesNotExist:
				pass
		if profile.facebook_activated == True:
			try:
				facebook_ads = Advertisement.objects.filter(advertisers__in=[profile])        
			except Advertisement.DoesNotExist:
				pass

	return render_to_response('profile.html', locals())

      
def auth_facebook(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
	
    code = request.GET.get('code')
    args = {
        'client_id': settings.FACEBOOK_APP_ID,
        'redirect_uri': request.build_absolute_uri('/auth/facebook/'),
        'scope': settings.FACEBOOK_PERMISSION_SCOPE,
    }
    
    if code != None:
        user = authenticate(token=code, request=request)
        if user != None:
		    activate_user = UserProfile.objects.get(user = user)
		    activate_user.facebook_activated = True
		    activate_user.save()
		    return HttpResponseRedirect('/auth/facebook/success/')
        else:
            return HttpResponseRedirect('/signin/')
    else:
        return HttpResponseRedirect('https://www.facebook.com/dialog/oauth?' + urllib.urlencode(args))


def auth_facebook_callback(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
    
    try:
        fb_user = FacebookUser.objects.get(user=request.user)
        thread.start_new_thread(batch_write_Mapfile, (request.user,))
    	return render_to_response('auth/facebook_auth_successful.html',{'fb_user':fb_user},
				context_instance = RequestContext(request))       
    except FacebookUser.DoesNotExist:
		return HttpResponseRedirect('/auth/facebook/')


def auth_twitter(request):
    # First set the variables for template context
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
    
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        HttpResponseRedirect('/signup/') 
    
    # Get consumer key along with oauth client key
    consumer, client = auth_attr()
    
    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])
        
    # Parse for request token
    request_token = dict(urlparse.parse_qsl(content))
    
    # Set request token as a session variable - 
    # auth_twitter_callback will also use it
    request.session['request_token'] = request_token

    # Return crendential url for social advertiser user in the template
    credential_url = "%s?oauth_token=%s" % (AUTHORIZATION_URL, request_token['oauth_token'])

    return HttpResponseRedirect(credential_url)


def auth_twitter_callback(request):
    # First set the variables for template context
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
        
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        HttpResponseRedirect('/signup/')

    # Twitter returns to query string variables after credential
    # One of them is oauth_verifier - aka. PIN
    oauth_verifier = request.GET.get('oauth_verifier')
    
    # Get consumer key along with the same oauth client key again
    consumer, client = auth_attr()
    
    # Retrieve request token of the auth session again 
    request_token = request.session['request_token']
    
    # Use request token to sign the request for access token
    # Access token will be used to identify the user for future
    # usage of Twitter in Social Advertiser, so store it in DB.    
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    
    # Get the api instance dedicated to this user
    api = twitter.Api(consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token['oauth_token'],
        access_token_secret=access_token['oauth_token_secret'])
    
    status = api.VerifyCredentials()
    status_dict = status.AsDict()
    
    # Create a new TwitterUser in database
    new_user = TwitterUser(user=request.user,
        access_token=access_token['oauth_token'],
        access_token_secret=access_token['oauth_token_secret'],
        twitter_user_id=status_dict['id'],
        twitter_screen_name=status_dict['screen_name'],
        followers_count=status_dict['followers_count'],
        friends_count=status_dict['friends_count'],
        statuses_count=status_dict['statuses_count'],
        protected=status_dict['protected'],
        account_created_at=status_dict['created_at'],
        account_timezone=status_dict['time_zone'],
        profile_image_url=status_dict['profile_image_url'],
        language=status_dict['lang'])
        
    new_user.save()
    
    # Assign user's twitter account is activated in the system
    profile = UserProfile.objects.get(user=request.user)
    profile.twitter_activated = True
    profile.save()
    
    """
    # Below code is for output test variables in command line
    print access_token.keys()
    print access_token.values()
    
    api = twitter.Api(consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token['oauth_token'],
        access_token_secret=access_token['oauth_token_secret'])
    
    print '______VerifyCredentials()______'
    status = api.VerifyCredentials()
    print status
    
    status_dict = status.AsDict()

    print status_dict['created_at']
    print status_dict['followers_count']
    print status_dict['friends_count']
    print status_dict['id']
    print status_dict['lang']
    print status_dict['screen_name']
    print status_dict['name']
    print status_dict['protected']
    print status_dict['statuses_count']
    print status_dict['time_zone']
    print status_dict['profile_image_url']
    
    print '______GetFriends()______'
    print api.GetFriends()
    print''
    
    print '______statuses______'
    statuses = api.GetPublicTimeline()
    print [s.user.name for s in statuses]
    
    statuses = api.GetUserTimeline(access_token['screen_name'])
    print [s.text for s in statuses]

    users = api.GetFriends()
    print [u.name for u in users]
    
    status = api.PostUpdate('This is first test of Social Advertiser')
    print status.text 
    """

    return render_to_response('auth/twitter_auth_successful.html', locals())
    
    
def auth_attr():
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    return consumer, client
    
