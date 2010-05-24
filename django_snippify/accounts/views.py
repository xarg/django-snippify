import time
import random
import hashlib

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, Http404

from django_snippify.models import Snippet
from django_snippify.utils import build_context

from models import UserProfile, UserFollow
from django_emailqueue.models import EmailQueue
from tagging.models import Tag

@login_required
def profile(request):
    """ View your own profile """
    tags = []
    snippets = {}
    snippets_all = snippets = Snippet.objects.filter(author=request.user)
    paginator = Paginator(snippets, 25)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    snippets = paginator.page(page).object_list
    for snippet in snippets_all:
        try:
            tag_list = Tag.objects.get_for_object(snippet)
            for tag in tag_list:
                if tag not in tags:
                    tags.append(tag)
        except:
            pass
    try:
        profile_data = request.user.get_profile()
    except UserProfile.DoesNotExist:
        profile_data = None

    try:
        followed_users = UserFollow.objects.select_related().filter(user=request.user).all()[0:14]
    except:
        followed_users = None

    try:
        followers = UserFollow.objects.select_related().filter(followed_user=request.user).all()[0:14]
    except:
        followers = None
    return render_to_response(
        'accounts/profile.html',
        {
            'profile': profile_data,
            'tags': tags,
            'snippets': snippets,
            'followed_users': followed_users,
            'followers': followers,
            'sidebared': True,
        },
        context_instance=build_context(request)
    )

@login_required
def edit(request):
    """ Edit your profile """
    if request.method == 'POST':
        form = EditForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            request.user.email = form.cleaned_data['email']
            request.user.save()

            profile = UserProfile.objects.get(user=request.user)
            profile.location = form.cleaned_data['location']
            profile.url = form.cleaned_data['url']
            profile.about = form.cleaned_data['about']
            profile.user_follows_you = form.cleaned_data['user_follows_you']
            profile.followed_user_created = form.cleaned_data['followed_user_created']
            profile.user_commented = form.cleaned_data['user_commented']
            #profile.user_shared = form.cleaned_data['user_shared']
            #profile.my_snippet_changed = form.cleaned_data['my_snippet_changed']
            profile.newsletter = form.cleaned_data['newsletter']
            profile.profile_privacy = form.cleaned_data['profile_privacy']
            profile.snippet_privacy = form.cleaned_data['snippet_privacy']

            profile.save()
            request.session['flash'] = ['Your profile has been updated', 'success']
    else:
        profile = UserProfile.objects.get(user=request.user)
        form = EditForm(initial = {
            'email': request.user.email,
            'location': profile.location,
            'url': profile.url,
            'about': profile.about,
            'user_follows_you': profile.user_follows_you,
            'followed_user_created': profile.followed_user_created,
            'user_commented': profile.user_commented,
            #'user_shared': profile.user_shared,
            #'my_snippet_changed': profile.my_snippet_changed,
            'newsletter': profile.newsletter,
            'profile_privacy': profile.profile_privacy,
            'snippet_privacy': profile.snippet_privacy,
        })
    return render_to_response('accounts/edit.html', {'form': form, }, context_instance=build_context(request))

@login_required
def refresh_key(request):
    """ Regenerate private key used with REST interface """
    profile = UserProfile.objects.get(user=request.user)
    profile.restkey = hashlib.sha1(str(random.random()) + 'snippify.me' + str(time.time())).hexdigest()
    profile.save()

    request.session['flash'] = ['Your private key has been refreshed, now update it in your plugin settings', 'success']
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def user(request, username=None):
    """ View user's profile """
    if username == request.user.username:
        return HttpResponseRedirect('/accounts/profile')
    userdata = get_object_or_404(User, username=username)
    profile = UserProfile.objects.filter(user=userdata).get()
    if profile.profile_privacy == 'private':
        raise Http404
    try:
        UserFollow.objects.filter(user=request.user, followed_user=userdata).get()
        is_following = True
    except:
        is_following = False
    if not user:
        raise Http404
    tags = []
    snippets = {}
    snippets_all = snippets = Snippet.objects.filter(author=userdata).filter(status='published').filter(privacy='public')
    paginator = Paginator(snippets, 25)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    snippets = paginator.page(page).object_list
    for snippet in snippets_all:
        try:
            tag_list = Tag.objects.get_for_object(snippet)
            for tag in tag_list:
                if tag not in tags:
                    tags.append(tag)
        except:
            pass
    try:
        followed_users = UserFollow.objects.select_related().filter(user=userdata).all()[0:14]
    except:
        followed_users = None

    try:
        followers = UserFollow.objects.select_related().filter(followed_user=userdata).all()[0:14]
    except:
        followers = None

    return render_to_response(
        'accounts/user.html', {
            'userdata': userdata,
            'profile': profile,
            'tags': tags,
            'snippets': snippets,
            'followed_users': followed_users,
            'followers': followers,
            'is_following': is_following,
            'sidebared': True,
        },
        context_instance=build_context(request)
    )

@login_required
def follow(request, follow_username = None):
    """ Follow a User """
    try:
        follow_user = User.objects.get(username = follow_username)
        followed_item = UserFollow()
        followed_item.user = request.user
        followed_item.followed_user = follow_user
        followed_item.save()
        try:
            profile = UserProfile.objects.get(user=follow_user)
            if profile.user_follows_you: #User wants to recieve a notification
                queue = EmailQueue(
                    mail_to=follow_user.email,
                    mail_subject="User started following you",
                    mail_body=render_to_string('emails/user_follows_you.txt', {
                        'user': follow_user,
                        'username_that_follows': request.user.username,
                        'SITE': request.META['HTTP_HOST']}
                    )
                )
                queue.save()
        except:
            pass
        request.session['flash'] = ['You started following ' + follow_user.username, 'success']
    except:
        request.session['flash'] = ['This user does not exist', 'error']
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def unfollow(request, follow_username=None):
    """ Stop following a user """
    try:
        follow_user = User.objects.get(username = follow_username)
        followed_item = UserFollow.objects.get(user = request.user, followed_user = follow_user);
        followed_item.delete()
        request.session['flash'] = ['You stoped following ' + follow_user.username, 'success']
    except:
        request.session['flash'] = ['This user does not exist', 'error']
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def followers(request, username=None):
    """ Who are your followers Jesus? """
    data = {}
    data['userdata'] = get_object_or_404(User, username=username)
    data['attribute'] = 'user'
    try:
        data['users'] = UserFollow.objects.select_related().filter(followed_user=data['userdata']).all()
    except:
        data['users'] = None
    return render_to_response('accounts/followers.html', data,  context_instance=build_context(request))

def following(request, username=None):
    """ Who is following username """
    data = {}
    data['userdata'] = get_object_or_404(User, username=username)
    data['attribute'] = 'followed_user'
    try:
        data['users'] = UserFollow.objects.select_related().filter(user=data['userdata']).all()
    except:
        data['users'] = None
    return render_to_response('accounts/following.html', data,  context_instance=build_context(request))

def unsubscribe(request):
    """ Unsubscribe from all notifications and newsletter """
    key = request.GET.get('key', None)
    if key:
        try:
            profile = UserProfile.objects.get(restkey = key)
            profile.user_follows_you = False
            profile.followed_user_created = False
            profile.user_commented = False
            profile.user_shared = False
            profile.my_snippet_changed = False
            profile.newsletter = False
            profile.save()
            request.session['flash'] = ['You have been unsubscribed from all emails', 'success'];
        except:
            request.session['flash'] = ['The key is not correct. Contact the administrator.', 'error'];
    return HttpResponseRedirect('/')

from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect

def login(request):
    if request.method == 'POST':
        pass
    else:
        return render_to_response('accounts/login.html', context_instance=build_context(request))
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.GET.get('next', reverse('snippify_index')))
