from django.contrib import admin
from app_auth.models import *

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_role', 'first_name', 'last_name', 
        'email', 'activation_key', 'is_staff', 'is_active', 
        'is_superuser', 'last_login', 'date_joined']
    list_select_related = True
    inlines = [
        UserProfileInline,
    ]

    def user_role(self, instance):
        return instance.get_profile().role
        
    def activation_key(self, instance):
        return instance.get_profile().activation_key
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(TwitterUser)
admin.site.register(FacebookUser)
