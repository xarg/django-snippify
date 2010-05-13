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
	url(r'^$', views.page_index, name="page_index"),
	url(r'^snippets/?$', views.index, name="snippet_index"),
	url(r'^(\d+)-?.*/?$', views.read, name="snippet_read"),
	url(r'^create/?$', views.create, name="snippet_create"),
	url(r'^update/(\d+)/?$', views.update, name="snippet_update"),
	url(r'^delete/(\d+)/?$', views.delete, name="snippet_delete"),
	url(r'^download/(\d+)/?$', views.download, name="snippet_download"),
	url(r'^history/(\d+)/?$', views.history, name="snippet_history"),
	url(r'^comment/(\d+)/?$', views.comment, name="snippet_comment"),
	#(r'^search-plugin.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'snippets/search-plugin.xml', 'extra_context': {'SITE': ''}}),
	url(r'^search/?$', views.search, name="snippet_search"),
	url(r'^suggest/?$', views.suggest, name="snippet_suggest"),

	url(r'^tag/(?P<tag>[^/]+)/?$', views.tag_view, name="tag_view"),
	url(r'^tag/(?P<tag>[^/]+)/(?P<username>[^/]+)/?$', views.tag_user, name="tag_user"),
	url(r'^tags/?$', views.tag_index, name="tag_index"),
	#(r'$', 'snippify.api.views.create'),
	url(r'^feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name="snippify_feeds"),
)
