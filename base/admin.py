from django.contrib import admin
from .models import User, UserProfile, Post, Comment, Hashtag, Notification, Follow


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "is_staff")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "description", "created_at")


admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Hashtag)
admin.site.register(Notification)
admin.site.register(Follow)
