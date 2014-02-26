from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from translations.models import Article, Language, Linguini_Translation
from datetime import datetime

def new_article(request):
    languages = Language.objects.all()

    return render(request, 'translations/new-article.html', {'languages':languages})

#locals

def submit_new_article(request):
    try:
        article_name = request.POST['article-name']
        article_source = request.POST['article-source']
        article_url = request.POST['article-url']
        article_difficulty = request.POST['article-difficulty']
        article_content = request.POST['article-content']
        article_origin_language = request.POST['article-origin-language']
        article_desired_languages = request.POST['article-desired-language']

    except (KeyError, Choice.DoesNotExist):
        #Redisplay the article creation form
        return render(request, 'translations/new-article.html', {
            'error_message' : "You didn't select a choice.",
            })
    else:
        new_article = Article.objects.create(name=article_name, content_source=article_source, source_url=article_url,
                                    difficulty=article_difficulty, content=article_content, origin_language_id=article_origin_language,
                                    date_added=datetime.now(), submitted_by_id=1)

        for desired_language_id in article_desired_languages:
            desired_translation = Linguini_Translation.objects.create(article=new_article, desired_language_id=desired_language_id)


        return HttpResponseRedirect(reverse('translations:articles'))

class ArticleView(generic.DetailView):
    model = Article
    template_name = 'translations/article-detail.html'

class ArticleListView(generic.ListView):
    template_name = 'translations/article-list.html'

    def get_queryset(self):
        """Return the last five published polls."""
        return Article.objects.order_by('-date_added')
