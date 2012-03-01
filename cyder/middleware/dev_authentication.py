from django.contrib.auth.models import User

from cyder.core.container.models import Container

class DevAuthenticationMiddleware(object):

    def process_request(self, request):

        # login as development user
        if request.user.is_anonymous():
            try:
                user = User.objects.get(username='development')
                request.user = user
            except:
                # manually create development user if not created already
                request.user = User()
                request.user.username = 'development'
                request.user.first_name = 'development'
                request.user.last_name = 'development'
                request.user.email = 'development@foo.bar.com'
                request.user.is_superuser = True
                request.user.backend = 'django.contrib.auth.backends.ModelBackend'
                request.user.save()

            # set session container on login to user's default container
            default_container = request.user.get_profile().default_container
            if not default_container:
                request.session.container = Container.objects.get(id=0)
            else:
                request.session.container = Container.objects.get(id=default_container.id)

        else:
            return None
