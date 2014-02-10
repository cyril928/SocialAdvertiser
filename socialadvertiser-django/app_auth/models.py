import datetime
import random
import re
import hashlib

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save


class RegistrationManager(models.Manager):
    def create_inactive_user(self, role, username, first_name, last_name, password, email):
                             
        new_user = User.objects.create_user(username, email, password)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.is_active = False
        new_user.save() 
        new_profile = self.create_profile(new_user, role)

        current_site = Site.objects.get_current()
        activation_url = ''.join(['%s%s%s%s%s' % ('http://', current_site, '/signup/', new_profile.activation_key, '/')])
        fullname = ''.join(['%s %s' % (first_name, last_name)])
        
        subject = render_to_string('auth/activation_email_subject.html', 
            { 'site': current_site })
        subject = ''.join(subject.splitlines())
        message = render_to_string('auth/activation_email.html',
            { 'user': fullname, 'activation_url': activation_url })

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        except smtplib.SMTPException:
            return HttpResponse('An error oocured. Please try again.')
        
        return new_profile
        
    def create_profile(self, user, role):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt+user.username).hexdigest()
        
        return self.create(user=user, role=role, activation_key=activation_key)
                           
    def activate_user(self, activation_key):
        SHA1_RE = re.compile('^[a-f0-9]{40}$')
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return None
            user = profile.user
            if user.is_active:
                return None
            user.is_active = True
            user.save()
            return profile
            
        return None

    
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    role = models.CharField(max_length=16)
    twitter_activated = models.BooleanField(default=False)
    facebook_activated = models.BooleanField(default=False)
    activation_key = models.CharField(_('activation key'), max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        
    def __unicode__(self):
        return "%s" % self.user
 
   
class TwitterUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    access_token_secret = models.CharField(max_length=255, blank=True, null=True)
    twitter_user_id = models.IntegerField(blank=True, null=True, editable=False)
    twitter_screen_name = models.CharField(max_length=255, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    friends_count = models.IntegerField(blank=True, null=True)
    statuses_count = models.IntegerField(blank=True, null=True)
    protected = models.NullBooleanField()
    account_created_at = models.CharField(max_length=128, blank=True, null=True)
    account_timezone = models.CharField(max_length=32, blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    language = models.CharField(max_length=16, blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.user
    

class FacebookUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    facebook_id = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=50,default='') 
    access_token = models.CharField(max_length=150, blank=True, null=True)  
    contacts = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(default=0)	
	
    def __unicode__(self):
        return "%s" % self.user
