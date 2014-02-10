from django.db import models
from django.contrib.auth.models import User

from app_auth.models import *


class Advertisement(models.Model):
    merchant = models.ForeignKey(UserProfile, unique=True, related_name='Merchant', blank=True, null=True)
    advertisers = models.ManyToManyField(UserProfile, related_name='Advertiser', blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_details = models.TextField(blank=True, null=True)
    suggested_post = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    age_range = models.CharField(max_length=128, blank=True, null=True)    
    number_of_contacts = models.CharField(max_length=64, blank=True, null=True)
    location = models.CharField(max_length=64, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    already_recommended = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s's %s" % (self.merchant, self.product_name)
        
    def get_absolute_url(self):
        return "ad/%s" % self.id

