from django.db import models
from django.contrib.auth.models import User

class Language(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    users = models.ManyToManyField(User, through='Language_Proficiency')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.country)

class Language_Proficiency(models.Model):
    ['Beginner', 'Intermediate','Fluent', 'Native Speaker']
    BEGINNER = 'BEG'
    INTERMEDIATE = 'INT'
    FLUENT = 'FLU'
    NATIVE_SPEAKER = 'NAT'
    PROFICIENCY_CHOICES = (
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (FLUENT, 'Fluent'),
        (NATIVE_SPEAKER, 'Native Speaker'),
        )

    user = models.ForeignKey(User)
    language = models.ForeignKey('Language')
    proficiency = models.CharField(max_length=3, choices=PROFICIENCY_CHOICES, default='')

    def __unicode__(self):
        return "%s - %s - %s" % (self.user, self.language, self.proficiency)

class Article(models.Model):
    EASY = 'EAS'
    MEDIUM = 'MED'
    DIFFICULT = 'DIF'
    DIFFICULTY_CHOICES  = (
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (DIFFICULT, 'Difficult'),
        )

    name = models.CharField(max_length=200)
    content_source = models.CharField(max_length=200)
    source_url = models.URLField(max_length=200)
    difficulty = models.CharField(max_length=3,choices=DIFFICULTY_CHOICES)
    content = models.TextField()
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


class Translation_Chunk(models.Model):
    user = models.ForeignKey(User)
    sentences = models.ManyToManyField('Sentence')
    translation = models.TextField()
    date_submitted = models.DateTimeField()
    num_sent = models.IntegerField(default=1)

class Sentence(models.Model):
    linguini_trans = models.ForeignKey('Linguini_Translation')
    original = models.TextField()
    accepted_translation = models.TextField()
    best_attempt = models.TextField()
    translation_is_choosen = models.BooleanField(default=False)
    attempts_before_acceptance = models.IntegerField(default=0)

class Linguini_Translation(models.Model):
    article = models.ForeignKey('Article')
    desired_language = models.ForeignKey('Language')
    acceptance_threshold = models.IntegerField(default=1)
    date_completed = models.DateTimeField('date all sentences translated', null=True)
