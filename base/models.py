from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
import uuid


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField()
    description = models.TextField(null=True, blank=True)
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
        except:
            img = ''
        return img

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
        ordering = ['-created_at']