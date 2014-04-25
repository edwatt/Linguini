from django.conf.urls import patterns, url
from translations import views
from views import DirectTemplateView
from django.contrib.auth.decorators import user_passes_test

staff_required = user_passes_test(lambda u: u.is_staff, login_url="/translations/access-denied/")

urlpatterns = patterns('',
    url(r'^home/$', views.home, name='home'),
    url(r'^submit-new-article/$', views.submit_new_article, name='submit-new-article'),
    url(r'^new-article/$', views.new_article, name='new-article'),
    url(r'^articles/$', staff_required(views.ArticleListView.as_view()), name='article_list'),
    url(r'^article/(?P<pk>\d+)/$', views.article_detail, name='article'),
    url(r'^access-denied/$', DirectTemplateView.as_view(template_name='translations/access-denied.html'), name="access-denied"),
    url(r'^register/$', views.register, name="register"),
    url(r'^language-prof/$', views.language_prof, name="language-prof"),
    url(r'^user-translate/(?P<origin_pk>\d+)/(?P<dest_pk>\d+)/$', views.user_translate, name="user-translate"),
    url(r'^site-summary/$', views.site_summary, name='site-summary'),
)
