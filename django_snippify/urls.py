from django.conf.urls.defaults import *
from feeds import LatestSnippets, LatestTag, LatestUser
feeds = {
    'latest': LatestSnippets,
    'tag': LatestTag,
    'user': LatestUser,
}

#Django piston - doesn't work with CSRF
#from piston.resource import Resource
#from snippify.api.handlers import SnippetHandler, HttpBasicAuthentication
#snippet_handler = Resource(SnippetHandler)

import views
urlpatterns = patterns('',
    url(r'^$', views.page_index, name="snippify_index"),
    url(r'^snippets/?$', views.index, name="snippify_snippets"),
    url(r'^(\d+)-?.*/?$', views.read, name="snippify_read"),
    url(r'^create/?$', views.create, name="snippify_create"),
    url(r'^update/(\d+)/?$', views.update, name="snippify_update"),
    url(r'^delete/(\d+)/?$', views.delete, name="snippify_delete"),
    url(r'^download/(\d+)/?$', views.download, name="snippify_download"),
    url(r'^history/(\d+)/?$', views.history, name="snippify_history"),
    url(r'^comment/(\d+)/?$', views.comment, name="snippify_comment"),
    url(r'^search/?$', views.search, name="snippify_search"),
    url(r'^suggest/?$', views.suggest, name="snippify_suggest"),
        # Tags
    url(r'^tags/?$', views.tag_index, name="snippify_tag_index"),
    url(r'^tag/(?P<tag>[^/]+)/?$', views.tag_view, name="snippify_tag_read"),
    url(r'^tag/(?P<tag>[^/]+)/(?P<username>[^/]+)/?$', views.tag_user, name="snippify_tag_user"),

    url(r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name="snippify_feeds"),
    url(r'^search-plugin.xml$', 'django.views.generic.simple.direct_to_template',
        {'template': '/search-plugin.xml', 'extra_context': None}, name="snippify_search_plugin"),
)
