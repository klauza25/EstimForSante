from django import forms
from .models import Consultation, Patient, Ordonnance, Examen, Patient, Personnel, RendezVous
from .models import SEXE_CHOICES
from django.utils.translation import gettext as _
from .models import Paiement, Consultation, Examen, Ordonnance
from django.utils.translation import gettext_lazy as _
from decimal import Decimal




MOTIF_CHOICES = [
    ('', '--- Sélectionnez un motif ---'),
    
    # Général
    ('Consultation de routine', 'Consultation de routine'),
    ('Suivi médical régulier', 'Suivi médical régulier'),
    ('Demande de certificat médical', 'Demande de certificat médical'),
    ('Visite annuelle de contrôle', 'Visite annuelle de contrôle'),
    ('Bilan de santé', 'Bilan de santé'),
    
    # Symptômes
    ('Fièvre persistante', 'Fièvre persistante'),
    ('Douleur abdominale', 'Douleur abdominale'),
    ('Maux de tête fréquents', 'Maux de tête fréquents'),
    ('Douleur thoracique', 'Douleur thoracique'),
    ('Toux chronique', 'Toux chronique'),
    ('Fatigue générale', 'Fatigue générale'),
    ('Essoufflement', 'Essoufflement'),
    ('Vertiges', 'Vertiges'),
    ('Palpitations', 'Palpitations'),
    ('Douleur musculaire', 'Douleur musculaire'),

    # Traumato
    ('Entorse ou foulure', 'Entorse ou foulure'),
    ('Douleur articulaire', 'Douleur articulaire'),
    ('Fracture suspectée', 'Fracture suspectée'),
    ('Lumbago', 'Lumbago'),
    ('Chute récente', 'Chute récente'),

    # Psychologique
    ('Anxiété / stress', 'Anxiété / stress'),
    ('Troubles du sommeil', 'Troubles du sommeil'),
    ('Dépression présumée', 'Dépression présumée'),
    ('Suivi psychologique', 'Suivi psychologique'),
    ('Burn-out', 'Burn-out'),

    # Cardiovasculaire
    ('Hypertension artérielle', 'Hypertension artérielle'),
    ('Douleur cardiaque', 'Douleur cardiaque'),
    ('Suivi après infarctus', 'Suivi après infarctus'),

    # Pédiatrie
    ('Fièvre chez l’enfant', 'Fièvre chez l’enfant'),
    ('Vaccination', 'Vaccination'),
    ('Toux ou rhume', 'Toux ou rhume'),
    ('Suivi de croissance', 'Suivi de croissance'),

    # Gynécologique
    ('Douleurs menstruelles', 'Douleurs menstruelles'),
    ('Retard de règles', 'Retard de règles'),
    ('Suivi de grossesse', 'Suivi de grossesse'),
    ('Contraception', 'Contraception'),

    # Gériatrie
    ('Chutes répétées', 'Chutes répétées'),
    ('Diminution de mémoire', 'Diminution de mémoire'),
    ('Douleurs chroniques', 'Douleurs chroniques'),
]

# forms.py

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'patient',
            'motif',
            'description',
            'poids',
            'taille',
            'tension_artérielle',
            'temperature',
            'pouls',
            'diagnostic',
            'traitement',
            'note',
            'status',
            'type_consultation',  # ✅ Assurez-vous qu'il est bien là
        ]
        widgets = {
            'type_consultation': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'diagnostic': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'traitement': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'tension_artérielle': forms.TextInput(attrs={'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'pouls': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.type_consultation:
            self.fields['type_consultation'].initial = self.instance.type_consultation

# forms.py



# forms.py

from django import forms
from .models import Patient, SEXE_CHOICES
from django.utils.translation import gettext as _

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
            'nom': _("Nom"),
            'prenom': _("Prénom"),
            'date_naissance': _("Date de naissance"),
            'sexe': _("Sexe"),
            'telephone': _("Téléphone"),
            'email': _("Email"),
            'adresse': _("Adresse"),
            'poids': _("Poids (kg)"),
            'taille': _("Taille (cm)"),
            'groupe_sanguin': _("Groupe sanguin"),
            'tension_artérielle': _("Tension artérielle"),
            'allergies': _("Allergies"),
            'antecedents_medicaux': _("Antécédents médicaux"),
        }
        widgets = {
             'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'tension_artérielle': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'antecedents_medicaux': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance and date_naissance > forms.fields.datetime.date.today():
            raise forms.ValidationError(_("La date de naissance ne peut pas être dans le futur."))
        return date_naissance
    
    
    
class OrdonnanceForm(forms.ModelForm):
    # Liste des médicaments courants pour les suggestions
    COMMON_DRUGS = [
        'Paracétamol',
        'Ibuprofène',
        'Aspirine',
        'Amoxicilline',
        'Doliprane',
        'Efferalgan',
        'Spasfon',
        'Ventoline',
        'Augmentin',
        'Levothyrox'
    ]

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
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Posologie'
    )

    class Meta:
        model = Ordonnance
        fields = ['nom_medicament', 'posologie', 'duree', 'quantite', 'notes']
        widgets = {
            'duree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Durée du traitement (ex: 7 jours)'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantité prescrite'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes supplémentaires (optionnel)'
            })
        }
        
        labels = {
            'nom_medicament': 'Nom du médicament',
            'posologie': 'Posologie',
            'duree': 'Durée du traitement',
            'quantite': 'Quantité',
            'notes': 'Notes supplémentaires'
        }



class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nom', 'date_examen', 'resultat', 'statut']
        widgets = {
            'date_examen': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resultat': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class ResultatExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['resultat', 'statut']
        widgets = {
            'resultat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Résultat de l\'examen'
            }),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'resultat': 'Résultat',
            'statut': 'Statut',
        }
        


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




class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = [
            'consultation',
            'examen',
            'ordonnance',
            'montant_total',
            'montant_paye',
            'difference_rendue',
            'type_paiement',
            'numero_transaction',
            'status',
            'notes',
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
        # Initialize montant_total dynamically based on related objects
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

        # Calculate difference_rendue initially if montant_paye provided
        montant_paye = self.initial.get('montant_paye') or (self.instance.montant_paye if self.instance else None)
        if montant_paye is not None:
            diff = montant_paye - montant_du
            self.fields['difference_rendue'].initial = diff if diff > 0 else 0

    def clean(self):
        """
        Validate that at least one of consultation, examen, or ordonnance is selected,
        and update montant_total and difference_rendue dynamically.
        """
        cleaned_data = super().clean()
        consultation = cleaned_data.get('consultation')
        examen = cleaned_data.get('examen')
        ordonnance = cleaned_data.get('ordonnance')
        montant_paye = cleaned_data.get('montant_paye')

        if not any([consultation, examen, ordonnance]):
            raise forms.ValidationError(
                _("Vous devez sélectionner au moins l'un des éléments suivants : consultation, examen ou ordonnance.")
            )

        montant_du = 0
        if consultation:
            montant_du += consultation.get_montant_du()
        if examen:
            montant_du += examen.get_cout()
        

        cleaned_data['montant_total'] = montant_du

        if montant_paye is not None and montant_paye >= montant_du:
            cleaned_data['difference_rendue'] = montant_paye - montant_du
        else:
            cleaned_data['difference_rendue'] = 0

        return cleaned_data


# forms.py

class AssignationForm(forms.Form):
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