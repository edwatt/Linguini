from django.conf.urls import patterns, url
from translations import views

urlpatterns = patterns('',
    url(r'^submit-new-article/$', views.submit_new_article, name='submit-new-article'),
    url(r'^new-article/$', views.new_article, name='new-article'),
    url(r'^articles/$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^article/(?P<pk>\d+)/$', views.ArticleView.as_view(), name='article'),
)
