# clinique_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

from home.views import custom_logout


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # App principale "home"
    path('', include('home.urls')),  # Toutes les vues de home sont gérées dans home/urls.py
    
    # Gestion de l'authentification
    path('accounts/', include('django.contrib.auth.urls')),  # Login, Logout…

    # Module Protocole
    path('protocole/', include('Protocole.urls')),
    
    # Page de déconnexion personnalisée
]

# Support des fichiers média
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)