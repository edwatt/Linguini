from django.db import models
from django.contrib.auth.models import User

class Language(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    users = models.ManyToManyField(User, through='Language_Proficiency')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.country)

class Language_Proficiency(models.Model):
    user = models.ForeignKey(User)
    language = models.ForeignKey('Language')
    #implement w/ choices
    proficiency = models.IntegerField()

class Article(models.Model):
    name = models.CharField(max_length=200)
    content_source = models.CharField(max_length=200)
    source_url = models.URLField(max_length=200)
    #implement w/ choices
    difficulty = models.IntegerField()
    content = models.TextField()
    #full_translation (google, professional, etc)
    origin_language = models.ForeignKey('Language')
    date_added = models.DateTimeField()
    submitted_by = models.ForeignKey(User)

    def __unicode__(self):
        return "%s - %s" % (self.name, self.content_source)

class Translation_Attempt(models.Model):
    user = models.ForeignKey(User)
    sentence = models.ForeignKey('Sentence')
    translation = models.TextField()
    date_submitted = models.DateTimeField()

class Sentence(models.Model):
    linguini_trans = models.ForeignKey('Linguini_Translation')
    original = models.TextField()
    accepted_translation = models.TextField()
    best_attempt = models.TextField()
    translation_is_choosen = models.BooleanField()
    attempts_before_acceptance = models.IntegerField()

class Linguini_Translation(models.Model):
    article = models.ForeignKey('Article')
    desired_language = models.ForeignKey('Language')
    acceptance_threshold = models.IntegerField(default=0)
    date_completed = models.DateTimeField('date all sentences translated', null=True)
