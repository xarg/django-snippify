from django.db import models
from django.contrib.auth.models import User
from django_snippify.utils import extend

#Note: I don't like this hack.. investigate another way to do this
try:
	from settings import AUTH_PROFILE_MODULE
	if 'django_snippify' in AUTH_PROFILE_MODULE:#UserProfile is the AUTH_PROFILE_MODULE
		CLASS_TO_EXTEND = models.Model
	else:
		CLASS_TO_EXTEND = __import__(AUTH_PROFILE_MODULE)
except ImportError:
	import sys
	print "AUTH_PROFILE_MODULE must be set in settings"
	sys.exit(2)

PRIVACY_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private')
)

@extend(CLASS_TO_EXTEND)
class UserProfile:
	""" This model is required """

	user = models.ForeignKey(User, unique=True)

	location = models.CharField(max_length=50)
	url = models.URLField()
	about = models.CharField(max_length=500)

	"""	Private key for REST API """
	restkey = models.CharField(max_length=40)

	""" E-mail notifications """
	user_follows_you = models.BooleanField(default=True,
		help_text='A user started following you')
	followed_user_created = models.BooleanField(default=True,
		help_text='A user that you follow submited a snippet')
	user_commented = models.BooleanField(default=True,
		help_text='A user has commented on your snippet')
	user_shared = models.BooleanField(default=True,
		help_text='A user shared with you a snippet')
	my_snippet_changed = models.BooleanField(default=True,
		help_text='Your snippet was changed by someone else than you')

	""" Privacy settings """
	profile_privacy = models.CharField(
		max_length = 50,
		default = 'public',
		choices = PRIVACY_CHOICES
	)
	snippet_privacy = models.CharField(
		max_length = 50,
		default = 'public',
		choices = PRIVACY_CHOICES
	)
	newsletter = models.BooleanField(default=True)

class UserFollow(models.Model):
	""" A user can follow a User or Tag """

	user = models.ForeignKey(User, related_name='stalkers')
	followed_user = models.ForeignKey(User, related_name='victims')
