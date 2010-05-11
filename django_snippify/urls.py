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
	(r'^$', views.page_index),
	(r'snippets/?$', views.index),
	(r'(\d+)-?.*/?$', views.read),
	(r'create/?$', views.create),
	(r'update/(\d+)/?$', views.update),
	(r'delete/(\d+)/?$', views.delete),
	(r'download/(\d+)/?$', views.download),
	(r'history/(\d+)/?$', views.history),
	(r'comment/(\d+)/?$', views.comment),
	#(r'^search-plugin.xml$', 'django.views.generic.simple.direct_to_template', {'template': 'snippets/search-plugin.xml', 'extra_context': {'SITE': ''}}),
	(r'search/?$', views.search),
	(r'suggest/?$', views.suggest),

	(r'tag/(?P<tag>[^/]+)/?$', views.tag_view),
	(r'tag/(?P<tag>[^/]+)/(?P<username>[^/]+)/?$', views.tag_user),
	(r'tags/?$', views.tag_index),
	#(r'$', 'snippify.api.views.create'),
	(r'feeds/(?P<url>.*)/?$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)
