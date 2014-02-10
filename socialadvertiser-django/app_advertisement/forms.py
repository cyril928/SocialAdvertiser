from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from app_advertisement.models import *

INDUSTRY_CHOICES = (
    ('Arts & Crafts & Sewing', 'Arts & Crafts & Sewing'),
    ('Automotive', 'Automotive'),
    ('Baby', 'Baby'),
    ('Beauty', 'Beauty'),
    ('Books', 'Books'),
    ('Cell phones & accessories', 'Cell phones & accessories'),
    ('Clothing & accessories', 'Clothing & accessories'),
    ('Electronic', 'Electronic'),
    ('Grocery & Gourmet Food', 'Grocery & Gourmet Food'),
    ('Health & personal care', 'Health & personal care'),
    ('Home & Garden & pets', 'Home & Garden & pets'),
    ('Industrial & Scientific', 'Industrial & Scientific'),
    ('Jewelry', 'Jewelry'),
    ('Magazine subsriptions', 'Magazine subsriptions'),
    ('Movies & TV', 'Movies & TV'),
    ('Music', 'Music'),
    ('Musical Instruments', 'Musical Instruments'),
    ('Office products', 'Office products'),
    ('Shoes', 'Shoes'),
    ('Software', 'Software'),
    ('Sports & Outdoors', 'Sports & Outdoors'),
    ('Tools & Home Improvement', 'Tools & Home Improvement'),
    ('Toys & Games', 'Toys & Games'),
    ('Video Games', 'Video Games'),
    ('Watches', 'Watches'),
)

AGE_RANGE_CHOICES = (
    ('N/A', 'N/A'),
    ('age<13', 'Below 13'),
    ('13<=age<=19', '13~19'),
    ('20<=age<=30', '20~30'),
    ('30<=age<=40', '30~40'),
    ('40<=age<=50', '40~50'),
    ('50<=age<=60', '50~60'),
    ('age>60', 'Above 60'),
)

GENDER_CHOICES = (
    ('Female and Male', 'Female and Male'),
    ('Female', 'Female'),
    ('Male', 'Male'),
)

LOCATION_CHOICES = (
    ('N/A', 'N/A'),
    ('Taiwan', 'Taiwan'),
    ('International', 'International'),
)

NUMBER_OF_CONTACTS_CHOICES = (
    ('100<=contacts<=300', '100~300'),
    ('300<=contacts<=600', '300~600'),
    ('600<=contacts<=1000', '600~1,000'),
    ('1000<=contacts<=2000', '1,000~2,000'),
    ('2000<=contacts<=5000', '2,000~5,000'),
    ('5000<=contacts<=10000', '5,000~10,000'),
    ('contacts>10000', 'Above 10,000'),
)

class AdvertisementForm(forms.Form):
    industry = forms.ChoiceField(choices=INDUSTRY_CHOICES, label=_('Industry'))
    product_name = forms.CharField(max_length=100, widget=forms.TextInput(), label=_('Product Name'))
    product_details = forms.CharField(widget=forms.Textarea(), label=_('Details About Product')) 
    suggested_post = forms.CharField(widget=forms.Textarea(), label=_('Suggested Wall Post')) 
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label=_('Gender Preference'))
    age_range = forms.ChoiceField(choices=AGE_RANGE_CHOICES, label=_('Age Range Preference'))
    number_of_contacts = forms.ChoiceField(choices=NUMBER_OF_CONTACTS_CHOICES, label=_('Number of Contacts/Followers Preference'))
    location = forms.ChoiceField(choices=LOCATION_CHOICES, label=_('Location'))
    price = forms.RegexField(regex=r'^[0-9]+$', max_length=32, widget=forms.TextInput(), label=_('Advertisement Fee ($US/click)'))
    
    def save(self):
        data = self.cleaned_data
        new_ad = Advertisement(industry=data['industry'],
        	product_name=data['product_name'],
        	product_details=data['product_details'],
        	suggested_post=data['suggested_post'],
        	gender=data['gender'],
        	age_range=data['age_range'],
        	number_of_contacts=data['number_of_contacts'],
        	location=data['location'],
        	price=data['price'])
        return new_ad
