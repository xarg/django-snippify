import json
import difflib
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, get_lexer_by_name, LEXERS
from pygments.util import ClassNotFound

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from forms import SnippetForm
from models import Snippet, SnippetVersion, SnippetComment
from accounts.models import UserProfile, UserFollow
from utils import build_context, JsonResponse

def page_index(request):
    """ First page of the app. Shows latest 10 snippets. """
    snippets = Snippet.objects.all()[0:5]
    if snippets == None:
        snippets = []
    return render_to_response('pages/index.html',
        {'snippets': snippets, 'home_page': True },
        context_instance=build_context(request))

@login_required
def index(request):
    """ My snippets """
    snippets = Snippet.objects.filter(author=request.user)
    return render_to_response('django_snippify/index.html', {'snippets': snippets},
                            context_instance=build_context(request))

def read(request, id=None):
    """ View some snippet, a snippet can be private so check that too """
    snippet = get_object_or_404(Snippet, pk=id)
    if SnippetVersion.objects.filter(snippet = snippet).all():
        versions = True
    else:
        versions = False
    comments_paginator = Paginator(SnippetComment.objects.filter(snippet=snippet).all(), 2)
    try:
        comments = comments_paginator.page(int(request.GET.get('page', 1)))
    except EmptyPage:
        comments  = None

    snippet.highlight_body = snippet.highlight(snippet.body, get_lexer_by_name(snippet.lexer))
    return render_to_response('django_snippify/read.html', {
            'snippet': snippet,
            'comments': comments,
            'versions': versions,
            'lines': range(1, snippet.body.count('\n')+2),
        },
        context_instance=build_context(request)
    )

def _process(request, id=None):
    """ Create/Update snippet """

    if id is not None:#Update
        snippet = get_object_or_404(Snippet, pk=id)
        form = SnippetForm(instance=snippet)

        if request.user.id == snippet.author_id:
            request.session['flash'] = ['Access denied', 'error'];
            return HttpResponseRedirect('/accounts/profile/')

        if 'delete' in request.POST:
            snippet.delete()
            request.session['flash'] = ['#' + str(formData.pk) +' deleted successfuly', 'sucess']
            return HttpResponseRedirect('/accounts/profile/')

    else:#Create
        snippet = None
        form = SnippetForm()

    if request.method == 'POST':
        form = SnippetForm(request.POST)#Bounding form to the POST data
        if not form.is_valid(): # redirect to form with errors
            return render_to_response('process.html', {'form': form }, context_instance=build_context(request))

        formData = form.save(commit = False)
        formData.pk = snippet.pk

        if 'preview' in request.POST:
            data = {}
            data['title'] = formData.title;
            data['preview_body'] = highlight(formData.body, get_lexer_by_name(formData.lexer), HtmlFormatter(cssclass = 'source'))
            data['lines'] = range(1, formData.body.count('\n') + 2)
            data['form'] = form
            data['snippet'] = formData
            return render_to_response('djnago_snippify/process.html', data, context_instance=build_context(request))

        else:#save
            formData.author = request.user
            if not formData.lexer:
                try:
                    lexer = guess_lexer(formData.body)
                    for lex in LEXERS.itervalues():
                        if lexer.name == lex[1]:
                            formData.lexer = lex[2][0].lower()
                except ClassNotFound:
                    formData.lexer = 'text'
            formData.save()
            if snippet and snippet.body != formData.body:
                try:
                    last_version = SnippetVersion.objects.order_by('-version').filter(snippet = snippet).all()[0]
                    new_version = SnippetVersion(snippet = snippet, version = last_version.version + 1, body = snippet.body)
                    new_version.save()
                except:
                    create_version = SnippetVersion(snippet = snippet, version = 1, body = snippet.body)
                    create_version.save()
            request.session['flash'] = ['#%s %s successfuly' % (formData.pk, 'update' if id is not None else 'created'), 'sucess'];
            return HttpResponseRedirect('/accounts/profile/')
    else:
        return render_to_response('django_snippify/process.html', {'form': form, 'snippet': snippet }, context_instance=build_context(request))

@login_required
def update(request, id=None):
    """ Update snippet """
    return _process(request, id)

@login_required
def create(request):
    """ Create snippet"""
    return _process(request)

#This here should go to signal code
#
#try:
#    followers = UserFollow.objects.select_related().filter(followed_user=request.user).all()
#except:
#    followers = None
#if followers: # this is very inneficient - find some other way
#    for follower in followers:
#        profile = follower.user.get_profile();
#        if profile.followed_user_created: #User wants to recieve a notification
#            queue = EmailQueue(
#                mail_to=follower.user.email,
#                mail_subject="Followed user created a new snippet",
#                mail_body=render_to_string('emails/followed_user_created.txt', {
#                    'user': follower.user,
#                    'username': request.user.username,
#                    'SITE': request.META['HTTP_HOST']}
#                )
#            )
#            queue.save()

@login_required
def delete(request, id=None):
    snippet = get_object_or_404(Snippet, pk=id)
    if snippet.author_id == request.user.id or request.user.is_staff:
        snippet.delete()
        request.session['flash'] = ['#%s deleted succesfully' % id, 'success']
        return HttpResponseRedirect('/accounts/profile/')
    else:
        request.session['flash'] = ['Access denied', 'error']

def history(request, id = None):
    """ Show history list or display diff between two versions """
    snippet = get_object_or_404(Snippet, pk=id)
    if request.GET.get('v'):
        version = int(request.GET['v'])
        if version == 0:
            body = snippet.highlight(snippet.body, get_lexer_by_name(snippet.lexer))
        else:
            ver = get_object_or_404(SnippetVersion, snippet = snippet, version=version)
            body = snippet.highlight(ver.body, get_lexer_by_name(snippet.lexer))
        return render_to_response('django_snippify/version.html',
            {'snippet': snippet, 'version': version, 'body': body, 'lines': range(1, body.count('\n'))},
            context_instance=build_context(request))

    elif request.GET.get('v1') and request.GET.get('v2'):
        version1 = int(request.GET['v1'])
        version2 = int(request.GET['v2'])
        if version1 == 0:
            version1_label = 'current'
            body_1 = snippet.body
        else:
            version1_label = 'v' + str(version1)
            body_1 = get_object_or_404(SnippetVersion, snippet = snippet, version=version1).body
        if version2 == 0:
            version2_label = 'current'
            body_2 = snippet.body
        else:
            version2_label = 'v' + str(version2)
            body_2 = get_object_or_404(SnippetVersion, snippet = snippet, version=version2).body
        fromlines = str(body_1).splitlines(True)
        tolines = str(body_2).splitlines(True)
        if len(fromlines) >= len(tolines):
            no = len(fromlines)
        else:
            no = len(tolines)
        diffbody = ''
        for line in difflib.unified_diff(fromlines, tolines, fromfile=version1_label, tofile=version2_label):
            diffbody = diffbody + str(line)
        diffbody = snippet.highlight(diffbody, get_lexer_by_name('diff'))
        return render_to_response('django_snippify/diff.html', {
            'snippet': snippet,
            'version1': version1,
            'version2': version2,
            'diffbody': diffbody,
            'lines': range(1, diffbody.count('\n'))
        },
        context_instance=build_context(request))
    else:
        snippet_versions = SnippetVersion.objects.filter(snippet = snippet).all()
        return render_to_response('django_snippify/history_index.html', {'snippet': snippet, 'snippet_versions': snippet_versions},
                                context_instance=build_context(request))

def comment(request, id = None):
    """
    Create a new comment.
    Django comments framework (v1.2) doesn't have a simple ajax api.
    Only staff users can delete comments. Also only logged users can post.
    """
    if request.GET.get('delete'):
        if request.user.is_staff:
            get_object_or_404(SnippetComment, pk=id).delete()
            request.session['flash'] = ['Comment deleted succesfully', 'success'];
        else:
            request.session['flash'] = ['Permission denied', 'error'];
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/accounts/profile/'))
    else:
        data = {}
        snippet = get_object_or_404(Snippet, pk=id)
        if request.user.is_authenticated:
            body = request.POST.get('body')
            if body:
                comment = SnippetComment(snippet = snippet, user = request.user, body = body)
                comment.save()
                if snippet.author != request.user: # send notification if you are not the author
                    profile = UserProfile.objects.get(user=snippet.author)
                    if profile.user_commented: #User wants to recieve a notification
                        queue = EmailQueue(
                            mail_to=snippet.author.email,
                            mail_subject="Your snippet has been commented",
                            mail_body=render_to_string('emails/user_commented.txt', {
                                'user': snippet.author,
                                'username': request.user.username,
                                'comment': comment,
                                'snippet': snippet,
                                'SITE': request.META['HTTP_HOST']}
                            )
                        )
                        queue.save()
                data['content'] = render_to_string('elements/comment.html', {'comment': comment})
            else:
                data['error'] = 'Body field is required'
        else:
            data['error'] = 'You must login to post a comment'
        return JsonResponse(data)

def search(request):
    """ Fulltext search view. Uses whoosh """
    data = {}
    data['query'] = request.GET.get('q', '')
    paginator = Paginator(Snippet.indexer.search(data['query']).prefetch(), 25)
    data['results'] = paginator.page(int(request.GET.get('page', 1)))
    return render_to_response('django_snippify/search.html', data,
        context_instance=build_context(request))

def suggest(request):
    """
    Used with Firefox search plugin to suggest search results
    returns json
    """
    data = []
    query = request.GET.get('q', '')
    results = Snippet.indexer.search(query).prefetch()
    data.append(query)
    results_list = []
    for result in results:
        results_list.append(result.instance.title)
    data.append(results_list)
    return HttpResponse(json.dumps(data))

def download(request, id=None):
    """ Download snippet setting a file extension by guessing it's mimetype"""
    snippet = get_object_or_404(Snippet, pk=id)
    try:
        file_extention = get_lexer_by_name(snippet.lexer).filenames[0].split('*')[1]
        file_mimetype = get_lexer_by_name(snippet.lexer).mimetypes[0]
    except:
        file_extention = '.txt'
        file_mimetype = 'text/plain'
    filename = str(snippet.title).lower().replace(' ','_') + file_extention
    response = HttpResponse(snippet.body, content_type=file_mimetype)
    response['Content-Length'] = len(snippet.body)
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    return response

#Tag views
def tag_index(request):
    """ View all tags into a tag cloud """
    tags = Tag.objects.all()
    return render_to_response('tags/index.html', {},
        context_instance=build_context(request))

def tag_view(request, tag = None):
    """ View all snippets of a specific tag """
    try:
        tag_object = Tag.objects.get(name=tag)
        snippets = TaggedItem.objects.get_by_model(Snippet, tag_object)
    except:
        snippets = None
    return render_to_response('tags/view.html',
        {'tag': tag, 'snippets': snippets},
        context_instance=build_context(request))

def tag_user(request, tag = None, username = None):
    """ View all snippets of a tag of a user """
    try:
        tag_object = Tag.objects.get(name=tag)
        snippets = TaggedItem.objects.get_by_model(Snippet, tag_object)
    except:
        snippets = None
    return render_to_response('tags/view.html',
        {'tag': tag, 'snippets': snippets},
        context_instance=build_context(request))
