from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from translations.models import Article, Language, Linguini_Translation, Sentence
from datetime import datetime
from nltk import tokenize

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
        article_desired_languages = request.POST.getlist('article-desired-language')

    except (KeyError):
        #Redisplay the article creation form
        return render(request, 'translations/new-article.html', {
            'error_message' : "You didn't select a choice.",
            })
    else:
        new_article = Article.objects.create(name=article_name, content_source=article_source, source_url=article_url,
                                    difficulty=article_difficulty, content=article_content, origin_language_id=article_origin_language,
                                    date_added=datetime.now(), submitted_by_id=1)

        content_sentences = tokenize.sent_tokenize(article_content)

        for desired_language_id in article_desired_languages:
            desired_translation = Linguini_Translation.objects.create(article=new_article, desired_language_id=desired_language_id)
            for sentence in content_sentences:
                Sentence.objects.create(linguini_trans=desired_translation, original=sentence)

        return HttpResponseRedirect(reverse('translations:article_list'))


def article_detail(request, pk):
    try:
        article = Article.objects.get(pk=pk)

    except (KeyError, Article.DoesNotExist):
        #Redisplay the article creation form
        return render(request, 'translations/article-detail.html', {
            'error_message' : "Article doesn't exist.",
            })
    else:
        desired_languages = Language.objects.filter(linguini_translation__article=article)
        linguini_trans = Linguini_Translation.objects.filter(article=article)[0]
        sentences = Sentence.objects.filter(linguini_trans = linguini_trans).order_by('id')

    return render(request, 'translations/article-detail.html', {'article':article, 'desired_languages':desired_languages, 'sentences':sentences})

class ArticleView(generic.DetailView):
    model = Article
    template_name = 'translations/article-detail.html'

class ArticleListView(generic.ListView):
    template_name = 'translations/article-list.html'

    def get_queryset(self):
        """Return the last five published polls."""
        return Article.objects.order_by('-date_added')
