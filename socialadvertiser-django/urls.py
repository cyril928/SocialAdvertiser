from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
import django.contrib.auth.views

import app_auth.views
import app_advertisement.views

admin.autodiscover()

urlpatterns = patterns('',
	# Static files path (css etc..) Usage: "/static/css/default.css"
	(r'^static/(?P<path>.*)$', 'django.views.static.serve', 
		{ 'document_root': settings.STATICFILES_DIRS } ),
      
	# Homepage URL
	url(r'^$', 'app_content.views.home', name='home'),
    
    # Authentication URLs
	url(r'^signin/$', app_auth.views.signin, name='signin'),
    url(r'^signout/$', app_auth.views.signout, name='signout'),
    url(r'^signup/$', app_auth.views.signup, name='signup'),
    url(r'^signup/(?P<key>[a-f0-9]{40})/$', app_auth.views.activate, name='activate'),
    
    # Reset password URLs
    url(r'^reset/password/$', django.contrib.auth.views.password_reset, name='password_reset'),
    (r'^reset/password/done/$', django.contrib.auth.views.password_reset_done),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', django.contrib.auth.views.password_reset_confirm),
    (r'^reset/done/$', django.contrib.auth.views.password_reset_complete),
    
    url(r'^profile/$', app_auth.views.profile, name='profile'),
    
    url(r'^profile/ad/(?P<ad_id>[0-9]+)$', app_advertisement.views.ad_details, name='ad_details'),
    
    # Social network authentication URLs
    url(r'^auth/twitter/$', app_auth.views.auth_twitter, name='auth_twitter'),
    url(r'^auth/twitter/success/$',
        app_auth.views.auth_twitter_callback, name='auth_twitter_callback'),
    
	url(r'^auth/facebook/$', app_auth.views.auth_facebook, name='auth_facebook'),
    url(r'^auth/facebook/success/$',
        app_auth.views.auth_facebook_callback, name='auth_facebook_callback'),
    
    url(r'^create/$', app_advertisement.views.create_ad, name='create_ad'),
   
	# Post ad into social network
	url(r'^post/facebook/(?P<post_message>(\w+))$', app_advertisement.views.post_facebook, name='post_facebook'),
	url(r'^post/twitter/(?P<post_message>(\w+))$', app_advertisement.views.post_twitter, name='post_twitter'),	
	
	url(r'^invite/(?P<aid>[0-9]+)/(?P<uid>[0-9]+)$', app_advertisement.views.invite_distributor, name='invite_distributor'),
		 
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable admin:
    url(r'^admin/', include(admin.site.urls)),
)
