from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, get_lexer_by_name, LEXERS

from tagging.fields import TagField
from tagging.models import Tag

def _lexer_names():
    ret = []
    for lexer in LEXERS.itervalues():
        ret.append((lexer[2][0], lexer[1]))
    ret.sort()
    return tuple(ret)

class Snippet(models.Model):
    """ """
    author = models.ForeignKey(User)
    title = models.CharField(max_length = 200, help_text = 'Ex. Django URL middleware')
    description = models.TextField(blank = True, help_text = 'Short description of your snippet')
    lexer = models.CharField(
        max_length = 50,
        blank = True,
        choices = (_lexer_names()),
        help_text = 'Choose one language or let snippify find it for you'
    )
    body = models.TextField(help_text="Snippet code goes here")
    created_date = models.DateTimeField(default = datetime.now())
    updated_date = models.DateTimeField(blank = True, null=True)
    status = models.CharField(
        max_length = 50,
        default = 'published',
        choices = (
            ('published', 'Published'),
            ('unpublished', 'Unplublished')
        )
    )
    privacy = models.CharField(
        max_length = 50,
        default = 'public',
        choices = (
            ('public', 'Public'),
            ('private', 'Private')
        )
    )
    tags = TagField()
    via = models.CharField(max_length = 50, default = 'web')

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.lexer)

    def highlight(self, body = '', lexer = None):
        """ Parse a piece of text and hightlight it as html"""
        if not lexer:
            lexer = get_lexer_by_name(u'text')
        return highlight (body, lexer, HtmlFormatter(cssclass = 'source') )

    def get_absolute_url(self):
        return '/' + str(self.pk)

    class Meta:
        ordering = ['-created_date']

class SnippetComment(models.Model):
    """ """
    snippet = models.ForeignKey(Snippet)
    user = models.ForeignKey(User)
    body = models.TextField()
    created_date = models.DateTimeField(default=datetime.now())

    class Meta:
        ordering = ['created_date']

class SnippetVersion(models.Model):
    """ History for snippets! """
    snippet = models.ForeignKey(Snippet)
    version = models.IntegerField(default = 1)
    body = models.TextField()
    created_date = models.DateTimeField(default=datetime.now())

    class Meta:
        ordering = ['-version']
