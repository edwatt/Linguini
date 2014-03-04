from django.conf.urls import patterns, include, url
from translations import views

from django.contrib import admin
admin.autodiscover()

#view object is translations/views - see import above

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home, name='home'),
    url(r'^login/', views.site_login, name='login'),
    url(r'^logout/', views.site_logout, name='logout'),
    url(r'^translations/', include('translations.urls', namespace = "translations")),
    url(r'^admin/', include(admin.site.urls)),
)
