from django.utils import timezone
from django import forms
from .models import Consultation, Patient, Ordonnance, Examen, Patient, Personnel, RendezVous
from .models import SEXE_CHOICES
from django.utils.translation import gettext as _
from .models import Paiement, Consultation, Examen, Ordonnance
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


# forms.py

from django import forms
from .models import Patient, SEXE_CHOICES, Consultation, Examen, Ordonnance, RendezVous, Paiement
from django.utils.translation import gettext as _

# Choix de posologie pour les ordonnances
POSOLOGIE_CHOICES = [
    ('matin', 'Matin'),
    ('midi', 'Midi'),
    ('soir', 'Soir'),
    ('matin_midi', 'Matin et Midi'),
    ('midi_soir', 'Midi et Soir'),
    ('matin_soir', 'Matin et Soir'),
    ('matin_midi_soir', 'Matin, Midi et Soir'),
    ('au_besoin', 'Au besoin'),
    ('autre', 'Autre'),
]

# Liste des médicaments courants pour les suggestions
COMMON_DRUGS = [
    'Paracétamol', 'Ibuprofène', 'Aspirine', 'Amoxicilline',
    'Doliprane', 'Efferalgan', 'Spasfon', 'Ventoline', 'Augmentin', 'Levothyrox'
]

# Choix pour le motif de consultation
MOTIF_CHOICES = [
    # Pédiatrie
    ('Fièvre', 'Fièvre'),
    ('Vaccination', 'Vaccination'),
    ('Toux ou rhume', 'Toux ou rhume'),
    ('Suivi de croissance', 'Suivi de croissance'),
    # Gynécologie
    ('Douleurs menstruelles', 'Douleurs menstruelles'),
    ('Retard de règles', 'Retard de règles'),
    ('Suivi de grossesse', 'Suivi de grossesse'),
    ('Contraception', 'Contraception'),
    # Gériatrie
    ('Chutes répétées', 'Chutes répétées'),
    ('Diminution de mémoire', 'Diminution de mémoire'),
    ('Douleurs chroniques', 'Douleurs chroniques'),
    # Par défaut
    ('autre', 'Autre'),
]

# Formulaire pour les ordonnances médicales
class OrdonnanceForm(forms.ModelForm):
    nom_medicament = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du médicament',
            'list': 'common-drugs',
            'autocomplete': 'off'
        }),
        label='Nom du médicament'
    )
    posologie = forms.ChoiceField(
        choices=POSOLOGIE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Posologie'
    )

    class Meta:
        model = Ordonnance
        fields = ['nom_medicament', 'posologie', 'duree', 'quantite', 'notes']
        widgets = {
            'duree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 7 jours'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité prescrite'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes supplémentaires (optionnel)'}),
        }
        labels = {
            'nom_medicament': 'Nom du médicament',
            'posologie': 'Posologie',
            'duree': 'Durée du traitement',
            'quantite': 'Quantité prescrite',
            'notes': 'Notes complémentaires',
        }

# Formulaire pour ajouter ou modifier un examen médical
# forms.py

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nom', 'resultat', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'resultat': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nom': _('Nom de l’examen'),
            'resultat': _('Résultat'),
            'statut': _('Statut')
        }

# Formulaire pour la validation d'un examen (résultat + statut)
class ResultatExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['resultat', 'statut']
        widgets = {
            'resultat': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Résultat de l’examen'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'resultat': 'Résultat',
            'statut': 'Statut',
        }

# Formulaire pour les rendez-vous
class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['medecin', 'date_rendezvous', 'heure_debut', 'heure_fin', 'motif', 'status']
        labels = {
            'medecin': _('Médecin'),
            'date_rendezvous': _('Date du rendez-vous'),
            'heure_debut': _('Heure de début'),
            'heure_fin': _('Heure de fin'),
            'motif': _('Motif du rendez-vous'),
            'status': _('Statut')
        }
        widgets = {
            'date_rendezvous': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'medecin': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get("heure_debut")
        heure_fin = cleaned_data.get("heure_fin")

        if heure_debut and heure_fin and heure_debut >= heure_fin:
            raise forms.ValidationError(_("L'heure de début doit être antérieure à l'heure de fin."))
        return cleaned_data

# Formulaire pour les paiements
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = [
            'consultation', 'examen', 'ordonnance',
            'montant_total', 'montant_paye', 'difference_rendue',
            'type_paiement', 'numero_transaction', 'status', 'notes'
        ]
        labels = {
            'montant_total': _('Montant dû'),
            'montant_paye': _('Montant payé'),
            'difference_rendue': _('Différence rendue'),
            'type_paiement': _('Mode de paiement'),
            'numero_transaction': _('Numéro de transaction'),
            'status': _('Statut du paiement'),
            'notes': _('Notes complémentaires'),
            'consultation': _('Consultation'),
            'examen': _('Examen'),
            'ordonnance': _('Ordonnance'),
        }
        widgets = {
            'consultation': forms.Select(attrs={'class': 'form-select'}),
            'examen': forms.Select(attrs={'class': 'form-select'}),
            'ordonnance': forms.Select(attrs={'class': 'form-select'}),
            'montant_total': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'montant_paye': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'difference_rendue': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'readonly': True}),
            'type_paiement': forms.Select(attrs={'class': 'form-select'}),
            'numero_transaction': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.instance.utilisateur = user

        # Calcul du montant dû à l’initialisation du formulaire
        montant_du = 0
        consultation = self.initial.get('consultation') or self.instance.consultation
        examen = self.initial.get('examen') or self.instance.examen
        ordonnance = self.initial.get('ordonnance') or self.instance.ordonnance

        if consultation:
            montant_du += consultation.get_montant_du()
        if examen:
            montant_du += examen.get_cout()
        if ordonnance:
            montant_du += ordonnance.get_cout()

        self.fields['montant_total'].initial = montant_du

    def clean(self):
        cleaned_data = super().clean()
        consultation = cleaned_data.get('consultation')
        examen = cleaned_data.get('examen')
        ordonnance = cleaned_data.get('ordonnance')
        montant_paye = cleaned_data.get('montant_paye')

        if not any([consultation, examen, ordonnance]):
            raise forms.ValidationError(_("Vous devez sélectionner au moins l'un des éléments suivants : consultation, examen ou ordonnance."))

        montant_du = 0
        if consultation:
            montant_du += consultation.get_montant_du()
        if examen:
            montant_du += examen.get_cout()
        if ordonnance:
            montant_du += ordonnance.get_cout()

        self.cleaned_data['montant_total'] = montant_du

        if montant_paye is not None:
            self.cleaned_data['difference_rendue'] = montant_paye - montant_du
        else:
            self.cleaned_data['difference_rendue'] = 0

        return cleaned_data

# Formulaire pour les rendez-vous
class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['medecin', 'date_rendezvous', 'heure_debut', 'heure_fin', 'motif', 'status']
        labels = {
            'medecin': _('Médecin'),
            'date_rendezvous': _('Date du rendez-vous'),
            'heure_debut': _('Heure de début'),
            'heure_fin': _('Heure de fin'),
            'motif': _('Motif du rendez-vous'),
            'status': _('Statut')
        }
        widgets = {
            'date_rendezvous': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motif': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'medecin': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get("heure_debut")
        heure_fin = cleaned_data.get("heure_fin")

        if heure_debut and heure_fin and heure_debut >= heure_fin:
            raise forms.ValidationError(_("L'heure de début doit être antérieure à l'heure de fin."))
        return cleaned_data

# Formulaire pour les patients
class PatientForm(forms.ModelForm):
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Inconnu', 'Inconnu'),
    ]

    sexe = forms.ChoiceField(
        choices=SEXE_CHOICES,
        label=_("Sexe"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    groupe_sanguin = forms.ChoiceField(
        choices=GROUPE_SANGUIN_CHOICES,
        label=_("Groupe sanguin"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_naissance = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label=_("Date de naissance")
    )

    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'date_naissance', 'sexe',
            'telephone', 'email', 'adresse',
            'poids', 'taille', 'groupe_sanguin',
            'tension_artérielle', 'allergies', 'antecedents_medicaux'
        ]
        labels = {
            'nom': _('Nom'),
            'prenom': _('Prénom'),
            'date_naissance': _('Date de naissance'),
            'sexe': _('Sexe'),
            'telephone': _('Téléphone'),
            'email': _('Email'),
            'adresse': _('Adresse'),
            'poids': _('Poids (kg)'),
            'taille': _('Taille (cm)'),
            'groupe_sanguin': _('Groupe sanguin'),
            'tension_artérielle': _('Tension artérielle'),
            'allergies': _('Allergies'),
            'antecedents_medicaux': _('Antécédents médicaux'),
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'tension_artérielle': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'antecedents_medicaux': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance and date_naissance > forms.fields.datetime.date.today():
            raise forms.ValidationError(_("La date de naissance ne peut pas être dans le futur."))
        return date_naissance

# Formulaire pour la consultation
# forms.py


class ConsultationForm(forms.ModelForm):
    # Champ séparé pour le motif si besoin (optionnel)
    motif = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le motif de la consultation'
        }),
        label=_("Motif"),
        required=False
    )

    class Meta:
        model = Consultation
        fields = [
            'patient', 'medecin', 'infirmier', 'date_consultation',
            'type_consultation', 'motif', 'description',
            'poids', 'taille', 'tension_artérielle', 'temperature', 'pouls',
            'diagnostic', 'traitement', 'note', 'status'
        ]
        widgets = {
            'date_consultation': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medecin': forms.Select(attrs={'class': 'form-select'}),
            'infirmier': forms.Select(attrs={'class': 'form-select'}),
            'type_consultation': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Décrivez les symptômes ou la situation rapportée')
            }),
            'poids': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'tension_artérielle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 12/8'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'pouls': forms.NumberInput(attrs={'class': 'form-control'}),
            'diagnostic': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Diagnostic établi')
            }),
            'traitement': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Traitement prescrit')
            }),
            'note': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': _('Notes supplémentaires')
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'date_consultation': _('Date et heure'),
            'type_consultation': _('Type de consultation'),
            'description': _('Symptômes'),
            'diagnostic': _('Diagnostic'),
            'traitement': _('Traitement'),
            'note': _('Note'),
            'status': _('Statut'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrage dynamique des médecins et patients selon le rôle
        if user and user.role == 'medecin':
            personnel = user.personnel
            self.fields['medecin'].queryset = Personnel.objects.filter(user=user)
            self.fields['patient'].queryset = Patient.objects.filter(
                consultations__medecin=personnel
            ).distinct()
        elif user and user.role == 'infirmier':
            self.fields['medecin'].queryset = Personnel.objects.filter(role='Médecin')
            self.fields['patient'].queryset = Patient.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        date_consultation = cleaned_data.get('date_consultation')

        if date_consultation and date_consultation < timezone.now():
            raise forms.ValidationError(_("La date de consultation ne peut pas être dans le passé."))

        return cleaned_data
    
    
    
    # home/forms.py ✅ Ajoute ce code

from django import forms
from .models import Patient, Personnel

class AssignationForm(forms.Form):
    """
    Formulaire pour assigner un patient à un médecin.
    Utilisé par le personnel d'accueil.
    """
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Sélectionnez un patient"
    )
    medecin = forms.ModelChoiceField(
        queryset=Personnel.objects.filter(role='Médecin'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Sélectionnez un médecin"
    )