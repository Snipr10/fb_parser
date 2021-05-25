from django.db import models
from datetime import datetime
import pytz


class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()
    found_date = models.DateTimeField()
    repost_from = models.IntegerField()
    created_date = models.DateTimeField()
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    trust = models.IntegerField(null=True, blank=True)
    sphinx_id = models.IntegerField(default=0)
    updated = models.DateTimeField()
    last_modified = models.DateTimeField(default=datetime(1, 1, 1, 0, 0, tzinfo=pytz.UTC))
    content_hash = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        db_table = 'prsr_parser_fb_posts'


class PostContent(models.Model):
    post_id = models.IntegerField(primary_key=True)
    content = models.TextField()

    class Meta:
        db_table = 'prsr_parser_fb_posts_content'


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    sphinx_id = models.IntegerField(default=0)
    screen_name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sex = models.IntegerField(default=0)
    bdate = models.DateField()
    followers = models.IntegerField(default=0)
    last_modify = models.DateTimeField()

    class Meta:
        db_table = 'prsr_parser_fb_users'


class UserExt(models.Model):
    id = models.IntegerField(primary_key=True)
    city = models.CharField(max_length=255)
    home_town = models.CharField(max_length=255)
    education = models.TextField()
    job = models.TextField()

    class Meta:
        db_table = 'prsr_parser_fb_users_ext'


class Comment(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    root_comment_id = models.IntegerField()
    created_date = models.DateTimeField()
    likes = models.IntegerField(default=0)
    trust = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'prsr_parser_fb_comments'


class CommentContext(models.Model):
    id = models.IntegerField(primary_key=True)
    content = models.TextField()

    class Meta:
        db_table = 'prsr_parser_fb_comment_content'


# TODO add id
class CommentLike(models.Model):
    comment_id = models.IntegerField()
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    created_date = models.DateTimeField()

    class Meta:
        db_table = 'prsr_parser_fb_comment_likes'


# TODO add id
class Likes(models.Model):
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    created_date = models.DateTimeField()

    class Meta:
        db_table = 'prsr_parser_fb_likes'


class Photo(models.Model):
    id = models.IntegerField(primary_key=True)
    href = models.CharField(max_length=512)

    class Meta:
        db_table = 'prsr_parser_fb_photos'


class PostPhoto(models.Model):
    post_id = models.IntegerField()
    photo_id = models.IntegerField(primary_key=True)

    class Meta:
        db_table = 'prsr_parser_fb_posts_photos'


class PostTrust(models.Model):
    post_id = models.IntegerField(primary_key=True)
    trustword_id = models.IntegerField()
    trust = models.IntegerField()
    modify_date = models.DateTimeField()
    modify_by = models.IntegerField()

    class Meta:
        db_table = 'prsr_parser_fb_post_trust'


# TODO add id
class Repost(models.Model):
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    created_date = models.DateTimeField()

    class Meta:
        db_table = 'prsr_parser_fb_reposts'


# TODO add id
class Friends(models.Model):
    friend_id = models.IntegerField()
    user_id = models.IntegerField()
    created_date = models.DateTimeField()

    class Meta:
        db_table = 'prsr_parser_fb_users_friends'
