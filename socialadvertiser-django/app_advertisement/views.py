import MySQLdb
import urlparse
import twitter
import oauth2 as oauth
import urllib, simplejson
import thread

from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.conf import settings

from app_content.models import *
from app_auth.models import *
from app_auth.forms import *
from app_advertisement.forms import *
from app_advertisement.models import *


from app_advertisement.utils import *

@csrf_protect
def create_ad(request):
    context = RequestContext(request)
    ad_form = AdvertisementForm()
    form = SigninForm()
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    if request.method == 'POST':
        ad_form = AdvertisementForm(data=request.POST)
        if ad_form.is_valid():
            new_ad = ad_form.save()
            profile = UserProfile.objects.get(user=request.user)
            new_ad.merchant = profile
            new_ad.save()
            return render_to_response('ad/ad_created.html', locals())
    else:
        ad_form = AdvertisementForm()
        
    return render_to_response('ad/create_ad_form.html', 
        { 'ad_form': ad_form, 'form': form }, context_instance=context)
        
        
def ad_details(request, ad_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
        
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    ad = Advertisement.objects.get(pk=ad_id)
	
	#test = User.objects.get(username='1')
	#test1 = User.objects.get(username='tw1')
	
    facebook_suggestions = do_facebook_recommendation(user, profile)
    twitter_suggestions = do_twitter_recommendation(user, profile)
    
    #TODO: add already_recommended
    
    return render_to_response('ad/ad_details.html', locals())


def invite_distributor(request, aid, uid):
    if not request.user.is_authenticated():
	    return HttpResponseRedirect('/signin/')

    user = request.user
    profile = UserProfile.objects.get(user=user)

    ad = Advertisement.objects.get(pk=aid)
    user_dist = User.objects.get(pk=uid)
    profile_dist = UserProfile.objects.get(user=user_dist)
    ad.advertisers.add(profile_dist)
    ad.save()

    return render_to_response('ad/invitation_sent.html', locals())
 

def do_facebook_recommendation(user, profile):
    if profile.role == 'merchant':
        ads = Advertisement.objects.filter(merchant=profile)
        db = MySQLdb.connect(user='socialadvertiser', db='socialadvertiser', passwd='socialaddb', host='localhost')
        cursor = db.cursor()
        for ad in ads:
            if ad.already_recommended == False:
                #filter_rules:[gender,age_range,number_of_contacts,location]
                gender =  ad.gender
                age_range = ad.age_range
                number_of_contacts = ad.number_of_contacts
                location = ad.location
                industry = ad.industry

                gender_dict = {
	                'Male':' AND gender=\'male\'',
	                'Female':' AND gender=\'female\'', 
	                'Female and Male':'',
                }

                if age_range == 'N/A':
	                age_range = ''
                else:
                    age_range = ' AND ' + age_range

                location_dict = {
	                'N/A':'',
	                'Taiwan':' AND location LIKE \'%Taiwan%\'',
	                'International':' AND location NOT LIKE \'%Taiwan%\'',  
                }

                gender = gender_dict.get(gender)
                location = location_dict.get(location)

                substmt = ''.join(['WHERE %s %s %s %s' % (number_of_contacts, age_range, gender, location)])
                stmt = ''.join(['SELECT a.user_Id, b.uuid, b.`%s` FROM `app_auth_facebookuser` as a LEFT JOIN `userrank` AS b ON a.facebook_Id=b.uuid %s ORDER BY `%s` DESC;    ' % (industry, substmt, industry)])

                print 'substmt : %s' % substmt
                print 'stmt : %s' % stmt

                cursor.execute(stmt)
                ad_distributors = cursor.fetchall()
                print ad_distributors
				
        db.close()
        return ad_distributors


def do_twitter_recommendation(user, profile):
    if profile.role == 'merchant':
        ads = Advertisement.objects.filter(merchant=profile)
        db = MySQLdb.connect(user='socialadvertiser', db='socialadvertiser', passwd='socialaddb', host='localhost')
        cursor = db.cursor()
        for ad in ads:
            if ad.already_recommended == False:
                #filter_rules:[gender,age_range,number_of_contacts,location]
                followers_count = ad.number_of_contacts.replace('contacts', 'followers_count')
                location = ad.location
                industry = ad.industry

                location_dict = {
	                'N/A':'',
	                'Taiwan':' AND account_timezone LIKE \'%Taipei%\'',
	                'International':' AND account_timezone NOT LIKE \'%Taipei%\'',  
                }

                location = location_dict.get(location)

                substmt = ''.join(['WHERE %s %s' % (followers_count, location)])
                stmt = ''.join(['SELECT user_Id, twitter_user_Id, followers_count FROM `app_auth_twitteruser` %s ORDER BY followers_count DESC;    ' % (substmt)])

                print 'substmt : %s' % substmt
                print 'stmt : %s' % stmt

                cursor.execute(stmt)
                ad_distributors = cursor.fetchall()
                print ad_distributors
				
        db.close()
        return ad_distributors


def post_twitter(request, post_message):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
		
    user = request.user
    profile = UserProfile.objects.get(user=user)
    twitter_user = TwitterUser.objects.get(user=user)
    
    consumer_key = getattr(settings, 'CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'CONSUMER_SECRET', None)
    
    api = twitter.Api(consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=twitter_user.access_token,
        access_token_secret=twitter_user.access_token_secret)
        
    status = api.PostUpdate(post_message)
	
    return render_to_response('ad/tw_ad_posted.html', locals())	
	
	
def post_facebook(request, post_message):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/signin/')
	
	publish_ad(request.user, post_message)
	
	return render_to_response('ad/fb_ad_posted.html', locals())	
	
