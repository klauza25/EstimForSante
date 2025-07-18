# views.py - Module Protocole

from home.models import Personnel
from .middleware import ActiveUserMiddleware
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from io import BytesIO
from django.core.paginator import Paginator
import qrcode
import pytz
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from .models import Presence


# === FONCTIONS UTILITAIRES ===

def get_connected_users():
    """Renvoie les utilisateurs connectés actuellement via leurs sessions actives."""
    User = get_user_model()
    sessions = Session.objects.filter(expire_date__gte=now())
    user_ids = []

    for session in sessions:
        data = session.get_decoded()
        if '_auth_user_id' in data:
            user_ids.append(data['_auth_user_id'])

    return User.objects.filter(id__in=user_ids)


# === GÉNÉRATION DE QR CODE ===

def generate_qr_code(request):
    clinic_url = request.build_absolute_uri('/pointage/')
    qr = qrcode.make(clinic_url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")


# === POINTAGE DE PRÉSENCE ===

@login_required
def pointage_presence(request):
    employe = request.user
    today = now().date()
    brazzaville_tz = pytz.timezone('Africa/Brazzaville')

    presence, created = Presence.objects.get_or_create(
        employe=employe,
        arrivee__date=today,
        defaults={'arrivee': now()}
    )

    # Si présence déjà créée aujourd’hui, on met à jour le départ
    if not created and presence.depart is None:
        presence.depart = now()
        presence.save()

    # Conversion en fuseau horaire local (Brazzaville)
    arrivee_brazza = presence.arrivee.astimezone(brazzaville_tz)
    heure_arrivee = arrivee_brazza.strftime('%H:%M:%S')

    heure_depart = None
    if presence.depart:
        depart_brazza = presence.depart.astimezone(brazzaville_tz)
        heure_depart = depart_brazza.strftime('%H:%M:%S')

    context = {
        'presence': presence,
        'heure_arrivee': heure_arrivee,
        'heure_depart': heure_depart,
        'is_arrivee': created or not presence.depart,
        'message': 'Départ enregistré' if presence.depart else 'Arrivée enregistrée',
    }

    return render(request, 'protocole/pointage_confirmation.html', context)


# === LISTE DES PRÉSENCES ===

@login_required
def liste_presences(request):
    role = request.GET.get("role", "")
    roles = Personnel.ROLE_CHOICES

    presences = Presence.objects.all().order_by("-arrivee")

    if role:
        presences = presences.filter(employe__role=role)

    paginator = Paginator(presences, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "protocole/index.html", {
        'presences': page_obj,
        'roles': roles,
        'role': role,
    })


# === GESTION DES UTILISATEURS CONNECTÉS ===

@login_required
def users_online(request):
    active_users = get_connected_users()
    return render(request, 'protocole/users_online.html', {
        'active_users': active_users,
        'count': active_users.count()
    })


@login_required
def manage_connected_users(request):
    User = get_user_model()
    sessions = Session.objects.filter(expire_date__gte=now())
    user_ids = []
    session_keys = {}

    for session in sessions:
        data = session.get_decoded()
        if '_auth_user_id' in data:
            user_id = data['_auth_user_id']
            user_ids.append(user_id)
            session_keys[user_id] = session.session_key

    users = User.objects.filter(id__in=user_ids)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        if user_id in session_keys:
            Session.objects.filter(session_key=session_keys[user_id]).delete()
            return redirect('manage_connected_users')

    return render(request, "protocole/manage_connected_users.html", {
        "users": users,
        "session_keys": session_keys
    })


@staff_member_required
def manage_connected_users_admin(request):
    return manage_connected_users(request)  # Réutilise la vue principale