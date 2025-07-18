from .models import Consultation
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

def consultations_notifications(request):
    if request.user.is_authenticated and request.user.role == 'medecin':
        consultations = Consultation.objects.filter(medecin=request.user, statut__in=['planifiee', 'en_cours']).order_by('date')
        consultation_list = []
        for consultation in consultations:
            consultation_list.append({
                'patient_name': f"{consultation.patient.nom} {consultation.patient.prenom}",
                'patient_age': consultation.patient.age,
                'date': consultation.date,
                'statut': consultation.statut,
                'detail_url': reverse('patient_detail', args=[consultation.patient.id]),
                'consultation_url': reverse('update_consultation', args=[consultation.id]),
            })
    else:
        consultation_list = []
    return {'consultations_notifications': consultation_list}

def users_online(request):
    User = get_user_model()
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_ids = []
    for session in sessions:
        data = session.get_decoded()
        uid = data.get('_auth_user_id')
        if uid:
            user_ids.append(uid)
    active_users = User.objects.filter(id__in=user_ids)
    return {
        'active_users': active_users,
        'users_online_count': active_users.count(),
    }