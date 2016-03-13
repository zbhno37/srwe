from django.conf.urls import patterns, include, url
from rss import views as rss_views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'rss_news.views.home', name='home'),
    # url(r'^rss_news/', include('rss_news.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^addrss.htm', rss_views.render_addrss),
    url(r'^addclass.htm', rss_views.render_addclass),
    url(r'^rss/add$', rss_views.add_rss),
    url(r'^class/add$', rss_views.add_class),

    # test
    #url(r'^test$', rss_views.fetch_rss_update),
]
