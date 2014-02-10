from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from app_auth.forms import *

def home(request):
    if request.user.is_authenticated():
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect('/signup/')

    form = SigninForm()

    return render_to_response('index.html', locals())
