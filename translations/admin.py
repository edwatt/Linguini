from django.contrib import admin
from translations.models import Article, Language, Linguini_Translation, Language_Proficiency

admin.site.register(Article)
admin.site.register(Language)
admin.site.register(Linguini_Translation)
admin.site.register(Language_Proficiency)
