from django.contrib import admin
from backend.models import (
    User,
    UserHealthInformation
)

class UserHealthInformationInline(admin.TabularInline):
    model = UserHealthInformation

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','phone','first_name', 'last_name', 'city', 'email')
    inlines = [UserHealthInformationInline]
    
admin.site.register(User, UserAdmin)
