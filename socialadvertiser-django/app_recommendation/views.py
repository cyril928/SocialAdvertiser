# Create your views here.

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

def recommendation(request):
	user = request.user
	profile = UserProfile.object.get(user=user)
	if profile.role == 'merchant':
		ads = Advertisement.object.filter(merchant=profile)
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
				
				gender_dict={
					'Male':' AND gender=\'male\'' 
					'Female':' AND gender=\'female\'' 
					'Female and Male':''
				}

				if age_range == 'N/A':
					age_range = ''
				else age_range = ' AND '.age_range

				location_dict={
					'N/A':''
					'Taiwan':' AND location like \'%Taiwan%\''
					'International':' AND location not like \'%Taiwan%\''  
				}
				gender = gender_dict.get(gender)
				location = location_dict.get(location)

				#stmt = select uuid from 
				substmt = 'SELECT uuid from app_auth_facebookuser WHERE'.number_of_contacts.age_range.gender.location

				stmt = 'SELECT uuid FROM userrank ORDER BY '.industry.' WHERE uuid=('.substmt.');'
				cursor.execute(stmt)
				ad_distributors = cursor.fetchall()
#				for ad_distributor in ad_distributors:
					
			db.close()
			return ad_distributors
