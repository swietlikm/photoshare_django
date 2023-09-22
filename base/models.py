import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.safestring import mark_safe


class User(AbstractUser):

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        UserProfile.objects.get_or_create(user=self)


class UserProfile(models.Model):
    avatar = models.ImageField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')

    objects = models.Manager()

    def __str__(self):
        return f"@{self.user}"

    @property
    def avatar_url(self):
        try:
            img = self.avatar.url
        except ValueError:
            img = self.get_default_avatar()
        return img

    @staticmethod
    def get_default_avatar():
        url = settings.MEDIA_URL + 'default_user_avatar.jpg'
        return url


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='postlikes', blank=True)
    user = models.ForeignKey(User, related_name='posts', on_delete=models.DO_NOTHING)

    objects = models.Manager()

    def __str__(self):
        return self.user.username

    @property
    def image_url(self):
        try:
            img = self.image.url
        except ValueError:
            img = ''
        return img

    def image_preview(self):  # new
        return mark_safe(f'<img src = "{self.image_url}" width = "300"/>')

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_comments(self):
        return self.comments.count()

    class Meta:
        ordering = ['-created_at']


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    class Meta:
        unique_together = ['follower', 'following']


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.DO_NOTHING)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='commentlikes', blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"@{self.user} | {self.text}"

    class Meta:
        ordering = ['created_at']
