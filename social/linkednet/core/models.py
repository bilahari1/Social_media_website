from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import uuid
from datetime import datetime

User = get_user_model()


# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=10)
    profileimg = models.ImageField(upload_to='profile_images', default='pic.png')
    location = models.CharField(max_length=100, blank=True)
    tenth = models.FloatField(blank=True, default=0)
    twelfth = models.FloatField(blank=True, default=0)
    ug = models.FloatField(blank=True, default=0)
    pg = models.FloatField(blank=True, default=0)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user


class Company(models.Model):
    cid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=50, default=0)
    cname = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=30)
    website = models.CharField(max_length=200)

    def __str__(self):
        return self.cname
