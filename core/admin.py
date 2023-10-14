from django.contrib import admin
from .models import Profile, Post, Like_Post, Followers_Count

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Like_Post)
admin.site.register(Followers_Count)