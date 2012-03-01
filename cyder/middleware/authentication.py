from django.shortcuts import redirect

class AuthenticationMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() or request.path in (u'/login', u'/logout'):
            pass
        else:
            return redirect('/login')
