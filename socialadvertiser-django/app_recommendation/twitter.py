
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response

from app_content.models import *
from app_auth.models import *
from app_auth.forms import *
from app_advertisement.forms import *
from app_advertisement.models import *
import MySQLdb

def do_twitter_recommendation(user,profile):
    if profile.role == 'merchant':
		ads = Advertisement.objects.filter(merchant=profile)
		db = MySQLdb.connect(user='socialadvertiser', db='socialadvertiser', passwd='socialaddb', host='localhost')
		cursor = db.cursor()
		for ad in ads:
			if ad.already_recommended == False:
				#filter_rules:[gender,age_range,number_of_contacts,location]
				followers_count = ad.number_of_contacts
				location = ad.location
				industry = ad.industry
				
				location_dict = {
					'N/A':'',
					'Taiwan':' AND location LIKE \'%Taiwan%\'',
					'International':' AND location NOT LIKE \'%Taiwan%\'',  
				}
				
				location = location_dict.get(location)
				
				substmt = ''.join(['WHERE %s %s' % (number_of_contacts, location)])
				stmt = ''.join(['SELECT user_Id, twitter_user_Id, followers_count FROM `app_auth_twitteruser` %s ORDER BY followers_count DESC;    ' % (substmt)])

				print 'substmt : %s' % substmt
				print 'stmt : %s' % stmt
				
				cursor.execute(stmt)
				ad_distributors = cursor.fetchall()
				print ad_distributors
				
			db.close()
			return ad_distributors
	
