from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    last_display = ['user', 'date_of_birth', 'photo']
