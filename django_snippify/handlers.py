# PISTON DOESN'T SUPPORT CSRF BYPASS - FUCK IT
import json
from pygments.lexers import guess_lexer, LEXERS
from pygments.util import ClassNotFound

from django import forms
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from piston.handler import BaseHandler
from piston.utils import throttle, validate

from models import Snippet
from accounts.models import UserProfile
from forms import SnippetForm

class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet

class SnippetHandler(BaseHandler):
    allowed_methods = ('POST',)
    model = Snippet

    #@validate(SnippetForm)
    #@throttle (5, 10*60)
    def create(self, request):
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        body = request.POST.get('body', '')
        tags = request.POST.get('tags', '')
        lexer = 'text'
        return Snippet(title=title, description=description, body=body, tags=tags, lexer=lexer)

class HttpBasicAuthentication(object):
    """
        Authenficate by restkey from UserProfile
    """
    def __init__(self):
        pass
    def is_authenticated(self, request):
        """
        This method call the `is_authenticated` method of django
        User in django.contrib.auth.models.

        `is_authenticated`: Will be called when checking for
        authentication. It returns True if the user is authenticated
        False otherwise.
        """

        self.request = request
        try:
            UserProfile.objects.get(restkey=request.POST.get('RESTKEY'))
            return True
        except:
            return False
    def challenge(self):
        resp = HttpResponse("Authorization Required")
        resp['WWW-Authenticate'] = 'Basic realm="API"'
        resp.status_code = 401
        return resp


def _auth(request):
    key = request.META.get('HTTP_RESTKEY', None)
    if key:
        try:
            profile = UserProfile.objects.get(restkey=key)
            return User.objects.get(pk=profile.user.pk)
        except:
            return None
    else:
        return None

@csrf_exempt
def create(request):
    """ Expect a post """
    user = _auth(request)
    if user:
        data = json.loads(request.POST.get('data', '{}'))
        data['status'] = 'published'
        form = SnippetForm(data)
        if not form.is_valid():
            return HttpResponse('VALIDATION')
        try:
            lexer_obj = guess_lexer(data['body'])
            for lex in LEXERS.itervalues():
                if lexer_obj.name == lex[1]:
                    lexer = lex[2][0].lower()
                    break
        except ClassNotFound:
            lexer = u'text'
        try:
            snippet = Snippet(
                author = user,
                title = data['title'],
                description = data['description'],
                body=data['body'],
                tags=data['tags'],
                lexer=lexer,
                via=data['via'],
                privacy = data['privacy'],
                status = data['status']
            )
            snippet.save()
            return HttpResponse('SUCCESS')
        except:
            return HttpResponse('ERROR')
    else:
        return HttpResponse('NOT_AUTHORIZED')
