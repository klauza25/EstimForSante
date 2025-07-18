from django.urls import path
from .views import  users_online, generate_qr_code, pointage_presence
from Protocole import views as proto_views

urlpatterns = [
    path('pointage/', proto_views.pointage_presence, name='pointage_presence'),
    path('qr-code/', proto_views.generate_qr_code, name='generate_qr_code'),
    path('utilisateurs-en-ligne/', proto_views.users_online, name='users_online'),
    path('gestion-presences/', proto_views.manage_connected_users, name='manage_connected_users'),
    path('admin/gestion-presences/', proto_views.manage_connected_users_admin),
    path('historique-presence/', proto_views.liste_presences, name='liste_presences'),
]