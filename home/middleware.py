from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import User

# Stocker les utilisateurs actifs
ACTIVE_USERS = {}

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ACTIVE_USERS[request.user.username] = now()

        response = self.get_response(request)
        return response

    @staticmethod
    def get_active_users():
        """ Retourne la liste des utilisateurs connectés (actifs récemment). """
        threshold = now()  # Ajuster si besoin, ex: `now() - timedelta(minutes=5)`
        return [user for user, last_seen in ACTIVE_USERS.items() if last_seen >= threshold]
