from django.conf.urls.defaults import *
import views
urlpatterns = patterns('',
    url(r'profile/', views.profile, name='snippify_accounts_profile'),
    url(r'edit/', views.edit, name='snippify_accounts_edit'),
    url(r'follow/(\w+)/?', views.follow, name='snippify_accounts_follow'),
    url(r'unfollow/(\w+)/?', views.unfollow, name='snippify_accounts_unfollow'),
    url(r'followers/(\w+)/?', views.followers, name='snippify_accounts_followers'),
    url(r'following/(\w+)/?', views.following, name='snippify_accounts_following'),
    url(r'refresh_key/?', views.refresh_key, name='snippify_accounts_refresh_key'),
    url(r'unsubscribe/?',views.unsubscribe, name='snippify_accounts_unsubscribe'),
    url(r'login/?',views.login, name='snippify_accounts_login'),
    url(r'logout/?',views.logout, name='snippify_accounts_logout'),
    url(r'(\w+)/', views.user, name='snippify_accounts_user')
)
