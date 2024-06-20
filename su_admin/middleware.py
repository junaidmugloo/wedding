from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_urls = getattr(settings, 'RESTRICTED_URLS', [])

    def __call__(self, request):
        if not request.user.is_authenticated and request.path in self.restricted_urls:
            return redirect(reverse('front_login'))  # Adjust 'login' to the name of your login URL pattern

        response = self.get_response(request)
        return response