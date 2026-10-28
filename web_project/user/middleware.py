class JwtAuthenticationMiddleware:
    """Deprecated compatibility middleware.

    Authentication is now enforced by Django REST Framework on each API view.
    This no-op wrapper remains only so an older local settings module fails
    safely instead of importing the removed legacy JWT package.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
