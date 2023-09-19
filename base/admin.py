from django.contrib import admin
from .models import Post, Comment, UserProfile


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "description", "created_at")


admin.site.register(Comment)
admin.site.register(UserProfile)