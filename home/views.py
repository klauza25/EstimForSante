# views.py

# === IMPORTS ===
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now
from .middleware import ActiveUserMiddleware
from .utils import get_drug_info_from_fda
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q
from .models import STATUS_PAIEMENT_CHOICES, Ordonnance, Consultation, Paiement, Patient, Personnel, Examen, Medicament, RendezVous
from .forms import MOTIF_CHOICES, ConsultationForm, PaiementForm, PatientForm, OrdonnanceForm, ExamenForm, RendezVousForm, ResultatExamenForm
from django.contrib.auth import get_user_model, login, logout,authenticate
from django.core.exceptions import ValidationError
import logging
from django import forms
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.contrib.sessions.models import Session
import requests
from django.http import JsonResponse
from .models import Medicament
from django.utils.translation import gettext as _, gettext_lazy as _l


logger = logging.getLogger(__name__)
User = get_user_model()


# views.py


def get_drug_info_from_fda(drug_name):
    """
    Recherche des informations sur un médicament via l'API de la FDA
    """
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                return {
                    'generic': result.get('openfda', {}).get('generic_name', [''])[0],
                    'brand': result.get('openfda', {}).get('brand_name', [''])[0],
                    'indications': result.get('indications_and_usage', [''])[0],
                    'warnings': result.get('warnings', [''])[0],
                    'dosage': result.get('dosage_forms_and_administration', [''])[0],
                }
    except Exception as e:
        print(f"Erreur lors de la recherche du médicament : {e}")
    return None

# views.py



def rechercher_medicament(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        meds = Medicament.objects.filter(nom__icontains=query)[:10]
        for m in meds:
            results.append({
                'nom': m.nom,
                'prix': str(m.prix),
                'stock': m.stock
            })

    return JsonResponse(results, safe=False)
# === VUES D'ACCUEIL ET AUTHENTIFICATION ===
@login_required
def home(request):
    role = request.user.role
    if role == 'medecin':
        return redirect('dashboard_docteur')
    elif role == 'infirmier':
        return redirect('dashboard_infirmier')
    elif role == 'accueil':
        return redirect('dashboard_accueil')
    elif role == 'pharmacien':
        return redirect('dashboard_pharmacien')
    else:
        return redirect('admin:index')



def custom_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')

    

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        if password and len(password) < 6:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        return cleaned_data


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Compte créé avec succès. Vous pouvez vous connecter.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# === UTILITAIRES ===
def check_role(user):
    allowed_roles = {"accueil", "medecin"}
    return user.role in allowed_roles


# === GESTION DES UTILISATEURS ===
@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        email = request.POST.get('email')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')

        # Vérifications
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return render(request, 'create_user.html', {'roles': Personnel.role })

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'create_user.html', {'roles': Personnel.role })

        # Création de l'utilisateur
        user = User.objects.create_user(username=username, password=password, email=email, role=role)
        Personnel.objects.create(
            user=user,
            nom=nom,
            prenom=prenom,
            email=email
        )

        messages.success(request, "Utilisateur créé avec succès.")
        return redirect('admin:index')

    return render(request, 'create_user.html', {'roles': Personnel.ROLE_CHOICES})


# views.py

@login_required
def mes_consultations(request):
    """
    Affiche uniquement les consultations du médecin connecté
    """
    if request.user.role != 'medecin':
        messages.error(request, "Accès refusé.")
        return redirect('home')

    try:
        personnel = request.user.personnel
    except Personnel.DoesNotExist:
        messages.error(request, "Votre profil médecin n’existe pas.")
        return redirect('logout')

    # Récupère les consultations du médecin connecté
    consultations = Consultation.objects.filter(medecin=personnel).select_related('patient')

    return render(request, 'dashboard/mes_consultations.html', {
        'consultations': consultations
    })
# === DASHBOARD SELON RÔLE ===
# views.py

@login_required
def dashboard_docteur(request):
    """
    Tableau de bord spécifique au rôle Médecin.
    Affiche uniquement les données pertinentes pour le médecin connecté.
    """
    if request.user.role != 'medecin':
        messages.error(request, "Accès refusé : Vous devez être médecin.")
        return redirect('home')

    try:
        # Récupère le profil médecin de l'utilisateur
        personnel = request.user.personnel
    except Personnel.DoesNotExist:
        messages.error(request, "Votre compte médecin n'est pas complet.")
        return redirect('logout')

    # Données spécifiques au médecin connecté
    consultations = Consultation.objects.filter(medecin__user=request.user).select_related('patient', 'medecin')
    examens = Examen.objects.filter(consultation__medecin=personnel, statut='En attente').select_related('consultation__patient')
    rendez_vous = RendezVous.objects.filter(medecin=personnel, status='En attente')
    
    # Compteur de notifications
    count_notifications = consultations.exclude(status='Terminée').count()

    return render(request, 'dashboard/dashboard_docteur.html', {
        'consultations': consultations,
        'examens': examens,
        'rendez_vous': rendez_vous,
        'personnel': personnel,
        'patients': Patient.objects.all(),
        'count_notifications': count_notifications,
    })
    
    
@login_required
def dashboard_infirmier(request):
    if request.user.role != 'infirmier':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    
    # Récupérer les consultations en attente ou en cours
    consultations = Consultation.objects.filter(status__in=['Planifiée', 'En cours'])
    patients = Patient.objects.all()
    medecins = Personnel.objects.filter(role='Médecin')
    examens = Examen.objects.filter(statut="En attente")
    rendez_vous = RendezVous.objects.all()
    personnel = Personnel.objects.all()

    return render(request, 'dashboard/dashboard_infirmier.html', {
        'consultations': consultations,
        'patients': patients,
        'medecins': medecins,
        'examens': examens,
        'rendez_vous': rendez_vous,
        'personnel': personnel
    })


@login_required
def dashboard_accueil(request):
    if request.user.role != 'accueil':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    patients = Patient.objects.all()
    consultations = Consultation.objects.all()
    personnels = Personnel.objects.all()

    context = {
        'patients': patients,
        'consultations': consultations,
        'personnels': personnels
    }

    return render(request, 'dashboard/dashboard_accueil.html', context)

@login_required
def dashboard_pharmacien(request):
    
    return render(request, 'dashboard/dashboard_pharmacien.html')


# === PATIENTS ===
# views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from .models import Patient, Consultation, Personnel
from django.core.exceptions import PermissionDenied

@login_required
def liste_patients(request):
    """
    Vue pour afficher la liste des patients.
    Accès réservé aux rôles 'accueil', 'medecin', 'infirmier'
    """
    if request.user.role not in ['accueil', 'medecin', 'infirmier']:
        messages.error(request, "Accès refusé : Rôle non autorisé.")
        return redirect('home')

    # Filtrage
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by("-date_naissance")

    # Recherche par nom ou téléphone
    if query:
        patients = patients.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(telephone__icontains=query)
        )

    # Pagination
    paginator = Paginator(patients, 6)  # 10 patients par page
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Statistiques (optionnelles)
    total_patients = patients.count()
    hommes = patients.filter(sexe='Homme').count()
    femmes = patients.filter(sexe='Femme').count()

    return render(request, 'dashboard/liste_patients.html', {
        'patients': page_obj,
        'total_patients': total_patients,
        'hommes': hommes,
        'femmes': femmes,
        'query': query
    })

@login_required
def ajouter_patient(request):
    if not check_role(request.user):
        return HttpResponseForbidden("Accès refusé.")
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient ajouté avec succès !")
            return redirect('liste_patients')
    else:
        form = PatientForm()
    return render(request, 'dashboard/form_patient.html', {'form': form})


@login_required
def modifier_patient(request, patient_id):
    if not check_role(request.user):
        return HttpResponseForbidden("Accès refusé.")
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('liste_patients')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'dashboard/form_patientM.html', {'form': form})


@login_required
def supprimer_patient(request, patient_id):
    if not check_role(request.user):
        return HttpResponseForbidden("Accès refusé.")
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.delete()
        return redirect('liste_patients')
    return render(request, 'dashboard/confirmer_suppression.html', {'patient': patient})


# views.py

@login_required
def patient_detail(request, pk):
    """
    Affiche tous les détails d’un patient + ses actes médicaux.
    """
    patient = get_object_or_404(Patient, pk=pk)

    # Récupère toutes les consultations du patient
    consultations = Consultation.objects.filter(patient=patient).select_related(
        'medecin', 'patient'
    ).prefetch_related('ordonnance_set', 'examen_set')

    # Récupère toutes les ordonnances via les consultations
    ordonnances = Ordonnance.objects.filter(consultation__patient=patient).select_related(
        'consultation__medecin'
    )

    # Récupère tous les examens via les consultations
    examens = Examen.objects.filter(consultation__patient=patient).select_related(
        'consultation__medecin'
    )

    # Récupère tous les paiements (via consultation ou directement)
    paiements = Paiement.objects.filter(consultation__patient=patient).select_related(
        'consultation', 'consultation__medecin'
    )

    return render(request, 'dashboard/patient_detail.html', {
        'patient': patient,
        'consultations': consultations,
        'ordonnances': ordonnances,
        'examens': examens,
        'paiements': paiements,
    })

# === CONSULTATIONS ===
@login_required
def create_consultation(request):
    if request.user.role not in ['medecin','infirmier']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    motif_values = [choice[1] for choice in MOTIF_CHOICES if choice[0]]
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.medecin = get_object_or_404(Personnel, user=request.user)
            consultation.save()
            messages.success(request, "Consultation créée avec succès.")
            return redirect('liste_consultations')
    else:
        form = ConsultationForm()
    return render(request, 'dashboard/create_consultation.html', {
        'form': form,
        'motif_values': motif_values
    })

@login_required
def liste_ordonnances(request, patient_id=None):
    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
        ordonnances = Ordonnance.objects.filter(consultation__patient=patient)
    else:
        patient = None
        ordonnances = Ordonnance.objects.all()

    # Pagination
    paginator = Paginator(ordonnances, 10)  # 10 ordonnances par page
    page = request.GET.get('page')
    try:
        ordonnances = paginator.page(page)
    except PageNotAnInteger:
        ordonnances = paginator.page(1)
    except EmptyPage:
        ordonnances = paginator.page(paginator.num_pages)

    # Récupération des informations FDA pour chaque ordonnance
    for ordonnance in ordonnances:
        ordonnance.fda_info = get_drug_info_from_fda(ordonnance.nom_medicament)

    return render(request, 'dashboard/ordonances.html', {
        'ordonnances': ordonnances,
        'patient': patient,
    })


@login_required
def update_consultation(request, consultation_id):
    """
    Vue pour modifier une consultation + afficher ses actes médicaux.
    """
    if request.user.role != 'medecin':
        messages.error(request, "Accès refusé : Vous devez être médecin.")
        return redirect('home')

    # Récupère la consultation
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'medecin'),
        id=consultation_id,
        medecin__user=request.user
    )

    # Récupère les données associées
    examens = Examen.objects.filter(consultation=consultation)
    ordonnances = Ordonnance.objects.filter(consultation=consultation)

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            form.save()
            messages.success(request, "Consultation mise à jour.")
            return redirect('consultation_detail', consultation_id=consultation.id)
    else:
        form = ConsultationForm(instance=consultation)

    return render(request, 'dashboard/update_consultation.html', {
        'form': form,
        'consultation': consultation,
        'examens': examens,
        'ordonnances': ordonnances
    })

# views.py
def consultation_detail(request, consultation_id):
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'medecin'),
        id=consultation_id
    )
    
    examens = Examen.objects.filter(consultation=consultation)
    ordonnances = Ordonnance.objects.filter(consultation=consultation)

    # ✅ Récupère TOUS les paiements liés à cette consultation
    paiements = Paiement.objects.filter(consultation=consultation).order_by('-date_paiement')
    paiement = paiements.first() if paiements.exists() else None

    return render(request, 'dashboard/consultation_detail.html', {
        'consultation': consultation,
        'examens': examens,
        'ordonnances': ordonnances,
        'paiement': paiement,
        'paiements': paiements,  # Pour afficher l'historique si besoin
    })

# === ORDONNANCES ===# views.py


@login_required
def creer_ordonnance(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)

    # Vérifie que seul le médecin peut créer une ordonnance
    if request.user.role != 'medecin' or consultation.medecin.user != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('consultation_detail', consultation_id=consultation.id)

    if request.method == "POST":
        form = OrdonnanceForm(request.POST)
        if form.is_valid():
            ordonnance = form.save(commit=False)
            ordonnance.consultation = consultation
            ordonnance.save()

            messages.success(request, "Ordonnance créée avec succès.")
            return redirect('consultation_detail', consultation_id=consultation.id)
    else:
        form = OrdonnanceForm()

    return render(request, 'ordonnances/creer.html', {
        'form': form,
        'consultation': consultation,
        'COMMON_DRUGS': OrdonnanceForm.COMMON_DRUGS,
        'title': _("Créer une ordonnance")
    })



@login_required
def detail_ordonnance(request, id):
    ordonnance = get_object_or_404(Ordonnance, id=id)
    if request.user.role not in ['medecin', 'pharmacien']:
        messages.error(request, "Vous n'avez pas l'autorisation.")
        return redirect('dashboard_accueil')
    try:
        fda_info = get_drug_info_from_fda(ordonnance.nom_medicament)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations FDA: {str(e)}")
        fda_info = None
        messages.warning(request, "Infos FDA indisponibles.")
    context = {
        'ordonnance': ordonnance,
        'consultation': ordonnance.consultation,
        'patient': ordonnance.consultation.patient,
        'fda_info': fda_info
    }
    return render(request, 'ordonnances/detail.html', context)


# === EXAMENS ===
# views.py

@login_required
def ajouter_examen(request, consultation_id):
    """
    Vue pour ajouter un examen à une consultation
    """
    if request.user.role not in ['medecin', 'infirmier']:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    consultation = get_object_or_404(Consultation, id=consultation_id)

    if request.method == "POST":
        form = ExamenForm(request.POST)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.consultation = consultation
            examen.patient = consultation.patient  # ✅ Récupère le patient depuis la consultation
            examen.save()
            messages.success(request, "Examen ajouté avec succès.")
            return redirect('consultation_detail', consultation_id=consultation.id)
        else:
            messages.error(request, "Erreur lors de l'ajout de l'examen.")
    else:
        form = ExamenForm()

    return render(request, 'examens/ajouter_examen.html', {
        'form': form,
        'consultation': consultation
    })



@login_required
def liste_examens(request):
    # Vérification des droits
    if request.user.role not in ['infirmier', 'medecin','accueil']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    # Filtre par statut
    statut = request.GET.get('statut', '').strip()
    examens = Examen.objects.select_related('consultation', 'consultation__patient').order_by('-id')

    if statut and statut in dict(Examen.STATUT_CHOICES).keys():
        examens = examens.filter(statut=statut)

    # Pagination
    paginator = Paginator(examens, 8)  # 8 examens par page
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Statistiques (optimisées pour réduire les requêtes)
    stats = {
        'total_examens': examens.count(),
        'examens_en_attente': examens.filter(statut='en_attente').count(),
        'examens_realises': examens.filter(statut='realise').count(),
        'total_consultations': Consultation.objects.count(),
        'total_ordonnances': Ordonnance.objects.count(),
    }

    context = {
        'examens': page_obj,
        'filtre_statut': statut,
        **stats,
    }

    return render(request, 'examens/liste_examens.html', context)


@login_required
def valider_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)

    if request.method == 'POST':
        form = ResultatExamenForm(request.POST, instance=examen)
        if form.is_valid():
            form.save()
            messages.success(request, "Examen mis à jour avec succès.")
            return redirect('liste_examens')
    else:
        form = ResultatExamenForm(instance=examen)

    return render(request, 'examens/valider_examen.html', {
        'form': form,
        'examen': examen,
    })


# === UTILITAIRES / API ===
@login_required
def search_drug(request, term):
    try:
        drug_info = get_drug_info_from_fda(term)
        if drug_info:
            return JsonResponse([drug_info], safe=False)
        return JsonResponse([], safe=False)
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de médicament: {str(e)}")
        return JsonResponse({"error": "Une erreur est survenue"}, status=500)


@login_required
def get_drug_info(request, drug_name):
    try:
        drug_info = get_drug_info_from_fda(drug_name)
        if drug_info:
            return JsonResponse(drug_info)
        return JsonResponse({"error": "Médicament non trouvé"}, status=404)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du médicament: {str(e)}")
        return JsonResponse({"error": "Une erreur est survenue"}, status=500)


# === SIGNAUX ===
@receiver(post_save, sender=Consultation)
def notify_status_change(sender, instance, created, **kwargs):
    if not created and instance.status == 'E':
        pass  # Implémenter notification si nécessaire


@login_required
def assignation_consultation(request):
    """
    View to assign a patient to a doctor for a consultation.
    Only reception staff ('accueil') are authorized.
    """
    consultation = Consultation.objects.filter(status__in=['Planifiée'])
    
    if request.user.role != 'accueil':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    patients = Patient.objects.all().order_by('-id')
    medecins = Personnel.objects.filter(role='Médecin')

    if request.method == "POST":
        patient_id = request.POST.get('patient')
        medecin_id = request.POST.get('medecin')  # lowercase key as expected

        # Validate fields
        if not patient_id or not medecin_id:
            messages.warning(request, "Veuillez sélectionner un patient et un médecin.")
            return render(request, 'dashboard/assignation_consultation.html', {
                'patients': patients,
                'medecins': medecins,
            })

        try:
            patient = get_object_or_404(Patient, id=patient_id)
            medecin = get_object_or_404(Personnel, id=medecin_id)

            # Create consultation
            Consultation.objects.create(
                patient=patient,
                medecin=medecin,
                motif="Consultation assignée",
                status='Planifier'  # short status code
            )
            messages.success(request, "Patient assigné avec succès au médecin.")

            return redirect('assignation_consultation')  # or another page
        except Exception as e:
            logger.error(f"Erreur lors de l'assignation : {str(e)}")
            messages.error(request, "Une erreur est survenue lors de l'assignation.")

    return render(request, 'dashboard/assignation_consultation.html', {
        'patients': patients,
        'medecins': medecins,
        'consultation': consultation,
    })
    


# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Consultation, Personnel, Patient
from .forms import AssignationForm

@login_required
def modifier_assignation(request, consultation_id):
    """
    Vue pour modifier l'assignation d'une consultation (patient ou médecin)
    """
    if request.user.role != 'accueil':
        messages.error(request, "Accès refusé.")
        return redirect('home')

    consultation = get_object_or_404(Consultation, id=consultation_id)

    if request.method == 'POST':
        form = AssignationForm(request.POST)
        if form.is_valid():
            consultation.patient = form.cleaned_data['patient']
            consultation.medecin = form.cleaned_data['medecin']
            consultation.status = 'Planifiée'  # Réinitialise le statut
            consultation.save()
            messages.success(request, "Assignation mise à jour avec succès.")
            return redirect('assignation_consultation')
    else:
        form = AssignationForm(initial={
            'patient': consultation.patient,
            'medecin': consultation.medecin
        })

    return render(request, 'dashboard/modifier_assignation.html', {
        'form': form,
        'consultation': consultation,
        'title': "Modifier l'assignation"
    }) 
    
 # views.py

@login_required
def supprimer_assignation(request, consultation_id):
    """
    Vue pour supprimer une consultation (assignation) si non terminée
    """
    if request.user.role != 'accueil':
        messages.error(request, "Accès refusé.")
        return redirect('home')

    consultation = get_object_or_404(Consultation, id=consultation_id)

    if request.method == 'POST':
        if consultation.status == 'Planifiée':
            consultation.delete()
            messages.success(request, "L'assignation a été supprimée.")
        else:
            messages.error(request, "Impossible de supprimer une consultation en cours ou terminée.")
        return redirect('assignation_consultation')

    return render(request, 'dashboard/confirmer_suppression_assignation.html', {
        'consultation': consultation
    })    
# @login_required
# def assignation_consultation(request):
#     if request.user.role != 'accueil':
#         messages.error(request, "Accès non autorisé.")
#         return redirect('home')

#     form = AssignationForm(request.POST or None)

#     if request.method == "POST":
#         if form.is_valid():
#             try:
#                 patient = form.cleaned_data['patient']
#                 medecin = form.cleaned_data['medecin']

#                 Consultation.objects.create(
#                     patient=patient,
#                     medecin=medecin,
#                     motif="Consultation assignée",
#                     status='P'
#                 )
#                 messages.success(request, "Patient assigné avec succès au médecin.")
#                 return redirect('assignation_consultation')
#             except Exception as e:
#                 logger.error(f"Erreur lors de l'assignation : {str(e)}")
#                 messages.error(request, "Une erreur est survenue lors de l'assignation.")
#         else:
#             messages.warning(request, "Formulaire invalide. Vérifiez vos choix.")

#     return render(request, 'dashboard/assignation_consultation.html', {
#         'form': form
#     })
    
@login_required
def reassignation_consultation(request):
    
    """
        View to reassign a consultation from a doctor to a nurse.
        Only doctors are authorized to reassign their consultations.
    """
    if request.user.role != 'Médecin':
        messages.error(request, "Access not authorized. Only doctors can reassign consultations.")
        return redirect('home')

    consultations = Consultation.objects.filter(medecin=request.user, status__in=['P', 'EC'])
    nurses = Personnel.objects.filter(role='Infirmier')

    if request.method == "POST":
        consultation_id = request.POST.get('consultation')
        nurse_id = request.POST.get('nurse')

        if not consultation_id or not nurse_id:
            messages.warning(request, "Please select a consultation and a nurse.")
            return render(request, 'dashboard/reassignation.html', {
                'consultations': consultations,
                'nurses': nurses,
            })

        try:
            consultation = get_object_or_404(Consultation, id=consultation_id, medecin=request.user)
            nurse = get_object_or_404(Personnel, id=nurse_id, role='Infirmier')

            # Update consultation
            consultation.infirmier = nurse
            consultation.status = 'R'  # 'R' for Reassigned
            consultation.save()

            messages.success(request, f"Consultation successfully reassigned to nurse {nurse.nom}.")
            return redirect('reassignation_consultation')
        except Exception as e:
            logger.error(f"Error during reassignment: {str(e)}")
            messages.error(request, "An error occurred during the reassignment.")

    return render(request, 'dashboard/reassignation_consultation.html', {
        'consultations': consultations,
        'nurses': nurses,
    })



# views.py

@login_required
def consultations(request):
    """
    Vue pour afficher la liste des consultations selon le rôle de l'utilisateur.
    """
    user = request.user

    # Filtrage par rôle
    if user.role == 'medecin':
        consultation_list = Consultation.objects.filter(medecin__user=user).select_related('patient', 'medecin')
    elif user.role == 'infirmier':
        consultation_list = Consultation.objects.filter(status__in=['Planifiée', 'En cours']).select_related('patient', 'medecin')
    else:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    # Pagination
    paginator = Paginator(consultation_list, 10)  # 10 consultations par page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/consultation.html', {
        'consultations': page_obj,
    })
    

@login_required
def manage_consultations(request):
    """
    Vue pour gérer les consultations.
    """
    if request.user.role != 'medecin':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')
    # Récupérer les consultations assignées au médecin connecté
    consultations = Consultation.objects.filter(medecin__user=request.user)
    return render(request, 'dashboard/manage_consultations.html', {
        'consultations': consultations,
    })

@login_required
def delete_consultation(request, consultation_id):
    """
    Vue pour supprimer une consultation.
    Seul le médecin propriétaire de la consultation peut la supprimer.
    """
    consultation = get_object_or_404(Consultation, id=consultation_id)

    # Vérification des droits
    if request.user.role != 'medecin' or consultation.medecin.user != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette consultation.")
        return redirect('home')

    if request.method == 'POST':
        consultation.delete()
        messages.success(request, "La consultation a été supprimée avec succès.")
        return redirect('liste_consultations')  # ou une autre page

    # Si ce n'est pas une requête POST, on affiche une page de confirmation
    return render(request, 'dashboard/confirmer_suppression.html', {
        'consultation': consultation
    })


@login_required
def personnel_detail(request, pk):
    """
    Vue pour afficher les détails d'un membre du personnel.
    """
    personnel = get_object_or_404(Personnel, pk=pk)
    consultations = Consultation.objects.filter(medecin=personnel)

    return render(request, 'dashboard/personnel_detail.html', {
        'personnel': personnel,
        'consultations': consultations
    })


@login_required
def personnel_list(request):
    """
    Vue pour afficher la liste des membres du personnel.
    Filtre par rôle si un paramètre GET 'role' est fourni.
    """
    role = request.GET.get("role", "")  # Récupère le filtre depuis l'URL

    # Filtrer les personnels selon le rôle sélectionné
    if role:
        personnel_list = Personnel.objects.filter(role=role)
    else:
        personnel_list = Personnel.objects.all()

    # Pagination : 4 personnels par page
    paginator = Paginator(personnel_list, 4)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Si aucun résultat trouvé après filtrage
    if not page_obj.object_list and role:
        messages.info(request, f"Aucun personnel trouvé pour le rôle '{role}'.")

    return render(request, 'dashboard/liste_personnels.html', {
        'personnel': page_obj,
        'roles': Personnel.ROLE_CHOICES,
        'role': role
    })


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Votre compte est inactif.")
        else:
            messages.error(request, "Identifiants invalides.")
    return render(request, 'registration/login.html')

@login_required
def historique_clinique(request):
    patients = Patient.objects.all().order_by('-id')
    consultations = Consultation.objects.all().order_by('-date_consultation')
    ordonnances = Ordonnance.objects.all() # Add ordering
    personnels = Personnel.objects.all().order_by('nom')
    examens = Examen.objects.all().order_by('-date_examen')
    rendezvous = RendezVous.objects.all()

    context = {
        'patients': patients,
        'consultations': consultations,
        'ordonnances': ordonnances,
        'personnels': personnels,
        'examens': examens,
        'rendezvous_list': rendezvous,
    }

    return render(request, 'dashboard/historique.html', context)


# home/views.py



def is_staff_or_medecin(user):
    return user.is_staff or user.role == 'medecin'

def get_connected_users():
    """Récupère les utilisateurs actuellement connectés"""
    User = get_user_model()
    sessions = Session.objects.filter(expire_date__gte=now())
    user_ids = []

    for session in sessions:
        data = session.get_decoded()
        if '_auth_user_id' in data:
            user_ids.append(data['_auth_user_id'])

    return User.objects.filter(id__in=user_ids)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'medecin')
def users_online(request):
    active_users = get_connected_users()
    return render(request, 'dashboard/users_online.html', {
        'active_users': active_users,
        'count': active_users.count()
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'medecin')
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
        if user_id and user_id in session_keys:
            Session.objects.filter(session_key=session_keys[user_id]).delete()
            return redirect('users_online')

    return render(request, "dashboard/manage_connected_users.html", {
        "users": users,
        "session_keys": session_keys
    })
    
def create_rendezvous(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.patient = consultation.patient
            rdv.save()
            return redirect('rendezvous_detail', rdv.id)
    else:
        form = RendezVousForm()
    
    return render(request, 'dashboard/create_rendezvous.html', {
        'form': form,
        'consultation': consultation
    })


def rendezvous_detail(request, rendezvous_id):
    """
    Display the details of a specific RendezVous.
    """
    rendezvous = get_object_or_404(RendezVous, id=rendezvous_id)
    return render(request, 'dashboard/detail_rendezvous.html', {'rendezvous': rendezvous})


@login_required
def liste_rendezvous(request):
    """
    Vue pour afficher la liste des rendez-vous.
    Les utilisateurs peuvent filtrer par statut.
    Accès selon le rôle :
    - Médecin : ses propres rendez-vous
    - Accueil : tous les rendez-vous
    - Infirmier : uniquement consultation (pas de rendez-vous)
    """

    user = request.user

    # Vérification des droits d'accès
    if user.role not in ['medecin', 'accueil', 'infirmier']:
        messages.error(request, ("Accès refusé."))
        return redirect('home')

    # Filtrage par statut
    statut = request.GET.get('statut', '').strip()
    rendezvouses = RendezVous.objects.all().select_related('patient', 'medecin')

    # Si l'utilisateur est un médecin, il ne voit que ses rendez-vous
    if user.role == 'medecin':
        try:
            medecin = Personnel.objects.get(user=user)
            rendezvouses = rendezvouses.filter(medecin=medecin)
        except Personnel.DoesNotExist:
            messages.error(request, _("Aucun médecin trouvé pour cet utilisateur."))
            return redirect('home')

    # Filtre par statut si présent
    if statut and statut in dict(RendezVous.STATUS_CHOICES).keys():
        rendezvouses = rendezvouses.filter(status=statut)

    # Pagination
    paginator = Paginator(rendezvouses, 10)  # 10 rendez-vous par page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Statistiques optionnelles
    stats = {
        'total': rendezvouses.count(),
        'en_attente': rendezvouses.filter(status='En attente').count(),
        'confirme': rendezvouses.filter(status='Confirmé').count(),
        'annule': rendezvouses.filter(status='Annulé').count(),
        'termine': rendezvouses.filter(status='Terminé').count(),
    }

    return render(request, 'dashboard/liste_rendezvous.html', {
        'rendezvouses': page_obj,
        'filtre_statut': statut,
        'stats': stats
    })
    
# views.py
# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Consultation, Paiement
from .forms import PaiementForm

@login_required
def enregistrer_paiement(request, consultation_id=None):
    """
    Vue pour enregistrer un paiement lié à une consultation.
    Gère aussi les erreurs (paiement déjà existant).
    """
    if request.user.role not in ['accueil', 'medecin']:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    # Récupère la consultation
    consultation = get_object_or_404(Consultation, id=consultation_id)

    # Vérifie qu'il n'y a pas déjà un paiement
    if hasattr(consultation, 'paiement'):
        messages.warning(request, "Un paiement existe déjà pour cette consultation.")
        return redirect('consultation_detail', consultation_id=consultation.id)

    if request.method == "POST":
        form = PaiementForm(request.POST)
        if form.is_valid():
            montant_paye = form.cleaned_data.get('montant_paye', Decimal('0.00'))
            
            paiement = form.save(commit=False)
            paiement.consultation = consultation
            paiement.montant_total = consultation.get_montant_du()
            paiement.utilisateur = request.user
            paiement.status = 'Payé' if montant_paye >= paiement.montant_total else 'Partiellement payé'
            paiement.difference_rendue = montant_paye - paiement.montant_total
            paiement.save()

            messages.success(
                request,
                f"Paiement enregistré. Différence rendue : {paiement.difference_rendue} XAF"
            )
            return redirect('consultation_detail', consultation_id=consultation.id)
    else:
        initial_data = {
            'consultation': consultation,
            'montant_total': consultation.get_montant_du(),
        }
        form = PaiementForm(initial=initial_data)

    return render(request, 'dashboard/enregistrer_paiement.html', {
        'form': form,
        'consultation': consultation
    })


@login_required
def detail_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    return render(request, 'dashboard/detail_paiement.html', {
        'paiement': paiement
    })

# views.py

@login_required
def liste_paiements(request):
    if request.user.role not in ['accueil', 'medecin']:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    user = request.user
    paiements_list = Paiement.objects.select_related(
        'consultation__patient',
        'consultation__medecin'
    ).order_by('-date_paiement')

    # Filtre par statut
    statut = request.GET.get("statut", "").strip()
    if statut and statut in dict(STATUS_PAIEMENT_CHOICES).keys():
        paiements_list = paiements_list.filter(status=statut)

    # Filtre par patient
    patient_id = request.GET.get("patient", "").strip()
    if patient_id:
        paiements_list = paiements_list.filter(consultation__patient_id=patient_id)

    # Filtre par période
    periode = request.GET.get("periode", "").strip()
    from django.utils import timezone
    today = timezone.now().date()

    if periode == "today":
        paiements_list = paiements_list.filter(date_paiement__date=today)
    elif periode == "week":
        paiements_list = paiements_list.filter(date_paiement__week=today.isocalendar()[1])
    elif periode == "month":
        paiements_list = paiements_list.filter(date_paiement__month=today.month, date_paiement__year=today.year)

    # Pagination
    paginator = Paginator(paiements_list, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Statistiques
    stats = {
        'total': paiements_list.count(),
        'payes': paiements_list.filter(status='Payé').count(),
        'partiels': paiements_list.filter(status='Partiellement payé').count(),
        'non_payes': paiements_list.filter(status='Non payé').count(),
    }

    # Liste des patients pour le filtre
    patients = Patient.objects.all().order_by('nom')

    return render(request, 'dashboard/liste_paiements.html', {
        'paiements': page_obj,
        'stats': stats,
        'filtre_statut': statut,
        'filtre_patient': patient_id,
        'filtre_periode': periode,
        'patients': patients,
        'STATUS_PAIEMENT_CHOICES': STATUS_PAIEMENT_CHOICES,
    })
    
    
# views.py

@login_required
def caisse(request):
    if request.user.role not in ['accueil']:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    consultations = Consultation.objects.filter(status='Terminée', paiement__isnull=True)
    paiements = Paiement.objects.all().order_by('-date_paiement')

    return render(request, 'dashboard/caisse.html', {
        'consultations': consultations,
        'paiements': paiements,
    })
    
    
    
# views.py

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

def generate_pdf(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    patient = paiement.consultation.patient if paiement.consultation else None

    # Rendu du template HTML
    template = get_template('factures/paiement_pdf.html')
    context = {
        'paiement': paiement,
        'patient': patient,
    }
    html = template.render(context)

    # Conversion en PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{paiement.id}.pdf"'
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf, encoding='UTF-8')

    # Retourne le PDF
    pdf.seek(0)
    response.write(pdf.read())
    return response