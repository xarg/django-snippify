from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from models import Snippet, SnippetComment, SnippetVersion

class SnippetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@email.com', 'password')
        self.superuser = User.objects.create_superuser('superuser', 'superuser@email.com', 'password')

        self.client.login(username='user', password='password')

        self.snippet_text = Snippet.objects.create(
            author=self.user,
            title="Text file",
            description="Text file for testing",
            lexer="txt",
            body="""This is a text snippet
            this is is the second line
            """
        )
        self.snippet_python = Snippet.objects.create(
            author=self.user,
            title="Python snippet",
            description="Python snippet for testing",
            lexer="python",
            body="""Snippet body"""
        )


    """ Snippets tests """
    def test_basic_snippet(self):
        """ Add, update, remove, test if pygments is working"""
        response = self.client.get(reverse('snippify_create'))
        self.assertEqual(response.status_code, 200)
        
    def test_comment_snippet(self):
        """ Comment on a specific snippet """

    def test_history(self):
        """ Check history functionality """

    def test_search(self):
        """ Test the search results """

    def test_suggest(self):
        """ Test autosuggest """

    def test_download(self):
        """ Downloading snippet """

class PistonTest(TestCase):
    """ Testing django-piston integration """
    def test_snippets(self):
        """"""

class UserTest(TestCase):
    """ Users tests """
    def test_follow(self):
        """ Follow/Unfollow some user """

    def test_tag(self):
        """ See if user appears  """
