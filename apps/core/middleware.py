from django.shortcuts import redirect
from django.conf import settings


class PINAuthMiddleware:
    """
    Simple PIN-based authentication middleware.
    Checks if the user has authenticated via PIN in their session.
    Redirects unauthenticated requests to the PIN login page.
    """

    EXEMPT_URLS = ['/login/', '/logout/', '/static/', '/media/', '/admin/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._is_exempt(request.path):
            if not request.session.get('pin_authenticated', False):
                return redirect('login')
        return self.get_response(request)

    def _is_exempt(self, path):
        exempt = getattr(settings, 'PIN_AUTH_EXEMPT_URLS', self.EXEMPT_URLS)
        return any(path.startswith(url) for url in exempt)
