from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect

class DevAuthenticationMiddleware(object):

    def process_request(self, request):

        if request.user.is_anonymous():
            try:
                user = User.objects.get(username='development')
                request.user = user
            except:
                request.user = User()
                request.user.username = 'development'
                request.user.first_name = 'development'
                request.user.last_name = 'development'
                request.user.email = 'development@foo.bar.com'
                request.user.is_superuser = True
                request.user.backend = 'django.contrib.auth.backends.ModelBackend'
                request.user.save()
        else:
            return None
