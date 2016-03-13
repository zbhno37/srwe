from django.db import models

# Create your models here.

class RSSItem(models.Model):
    rss_id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=200)
    update_time = models.DateTimeField()

class ClassItem(models.Model):
    class_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)

class Subscription(models.Model):
    subscr_id = models.AutoField(primary_key=True)
    rss_id = models.ForeignKey(RSSItem)

class News(models.Model):
    news_id = models.AutoField(primary_key=True)
    rss_id = models.ForeignKey(RSSItem)
    pub_time = models.DateTimeField()
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    content = models.TextField()
    news_link = models.CharField(max_length=200)
    class_id = models.ForeignKey(ClassItem)
