from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from decimal import Decimal


# === CHOIX PARTAGÉS ===
USER_ROLE_CHOICES = [
    ('accueil', _('Accueil')),
    ('medecin', _('Médecin')),
    ('infirmier', _('Infirmier')),
    ('pharmacien', _('Pharmacien')),
]

PERSONNEL_ROLE_CHOICES = [(role[0].capitalize(), role[1]) for role in USER_ROLE_CHOICES]

SEXE_CHOICES = [
    ('M', 'Masculin'),
    ('F', 'Féminin'),
    ('Autre', 'Autre / Non binaire'),
]


# === MODELES ===
class User(AbstractUser):
    """
    Utilisateurs du système avec rôle spécifique.
    """
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='accueil')

    def clean(self):
        super().clean()
        if self.role not in dict(USER_ROLE_CHOICES):
            raise ValidationError(f"Invalid role: {self.role}")
        # Validation supplémentaire : date de naissance non future (si ajoutée)
        # if hasattr(self, 'date_naissance') and self.date_naissance > date.today():
        #     raise ValidationError(_("La date de naissance ne peut être dans le futur."))

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Patient(models.Model):
    """
    Représente un patient de la clinique.
    """
    GROUPE_SANGUIN_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('Inconnu', 'Inconnu'),
    ]

    nom = models.CharField(_('Nom'), max_length=100)
    prenom = models.CharField(_('Prénom'), max_length=100)
    date_naissance = models.DateField(_('Date de naissance'))
    sexe = models.CharField(_('Sexe'), max_length=10, choices=SEXE_CHOICES)
    telephone = models.CharField(_('Téléphone'), max_length=20)
    email = models.EmailField(_('Email'), blank=True, null=True)
    adresse = models.TextField(_('Adresse'), blank=True, null=True)
    
    # Informations médicales basiques
    poids = models.DecimalField(_('Poids (kg)'), max_digits=5, decimal_places=2, blank=True, null=True)
    taille = models.DecimalField(_('Taille (cm)'), max_digits=5, decimal_places=2, blank=True, null=True)
    groupe_sanguin = models.CharField(_('Groupe sanguin'), max_length=10, choices=GROUPE_SANGUIN_CHOICES, default='Inconnu')
    tension_artérielle = models.CharField(_('Tension artérielle'), max_length=20, blank=True, null=True, help_text="Ex: 12/8")
    allergies = models.TextField(_('Allergies'), blank=True, null=True)
    antecedents_medicaux = models.TextField(_('Antécédents médicaux'), blank=True, null=True, help_text=_("Antécédents médicaux importants"))

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < 
            (self.date_naissance.month, self.date_naissance.day)
        )

    def get_ordonnances(self):
        return Ordonnance.objects.filter(consultation__patient=self)

    class Meta:
        ordering = ['nom', 'prenom']


class Personnel(models.Model):
    """
    Représente un membre du personnel médical ou administratif.
    """
    ROLE_CHOICES = [
        ('Médecin', 'Médecin'),
        ('Infirmier', 'Infirmier'),
        ('Pharmacien', 'Pharmacien'),
        ('Accueil', 'Accueil'),
        # Ajoute d'autres rôles si besoin
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personnel"
    )
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)

    def save(self, *args, **kwargs):
        if self.user and self.user.role not in [r[0] for r in USER_ROLE_CHOICES]:
            raise ValueError("Only valid users can be linked to Personnel.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.role})"

    class Meta:
        verbose_name = _("Personnel")
        verbose_name_plural = _("Personnels")
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.utils import timezone

class Consultation(models.Model):
    """
    Représente une consultation médicale dans le système.
    """
    STATUS_CHOICES = [
        ('Planifier', _('Planifier')),
        ('En cours', _('En cours')),
        ('Terminer', _('Termier')),
        ('Annulée', _('Annulée')),
    ]

    # Correction : Ajout de 'Première consultation' et utilisation correcte des motifs
    TYPE_CONSULTATION_CHOICES = [
        ('Première consultation', _('Première consultation')),  # ✅ Ajouté ici
        ('Suivi', _('Suivi')),
        ('Urgence', _('Urgence')),
        ('Téléconsultation', _('Téléconsultation')),

        # Général
        ('Consultation de routine', _('Consultation de routine')),
        ('Suivi médical régulier', _('Suivi médical régulier')),
        ('Demande de certificat médical', _('Demande de certificat médical')),
        ('Visite annuelle de contrôle', _('Visite annuelle de contrôle')),
        ('Bilan de santé', _('Bilan de santé')),

        # Symptômes
        ('Fièvre persistante', _('Fièvre persistante')),
        ('Douleur abdominale', _('Douleur abdominale')),
        ('Maux de tête fréquents', _('Maux de tête fréquents')),
        ('Douleur thoracique', _('Douleur thoracique')),
        ('Toux chronique', _('Toux chronique')),
        ('Fatigue générale', _('Fatigue générale')),
        ('Essoufflement', _('Essoufflement')),
        ('Vertiges', _('Vertiges')),
        ('Palpitations', _('Palpitations')),
        ('Douleur musculaire', _('Douleur musculaire')),

        # Traumato
        ('Entorse ou foulure', _('Entorse ou foulure')),
        ('Douleur articulaire', _('Douleur articulaire')),
        ('Fracture suspectée', _('Fracture suspectée')),
        ('Lumbago', _('Lumbago')),
        ('Chute récente', _('Chute récente')),

        # Psychologique
        ('Anxiété / stress', _('Anxiété / stress')),
        ('Troubles du sommeil', _('Troubles du sommeil')),
        ('Dépression présumée', _('Dépression présumée')),
        ('Suivi psychologique', _('Suivi psychologique')),
        ('Burn-out', _('Burn-out')),

        # Cardiovasculaire
        ('Hypertension artérielle', _('Hypertension artérielle')),
        ('Douleur cardiaque', _('Douleur cardiaque')),
        ('Suivi après infarctus', _('Suivi après infarctus')),

        # Pédiatrie
        ('Fièvre chez l’enfant', _('Fièvre chez l’enfant')),
        ('Vaccination', _('Vaccination')),
        ('Toux ou rhume', _('Toux ou rhume')),
        ('Suivi de croissance', _('Suivi de croissance')),

        # Gynécologique
        ('Douleurs menstruelles', _('Douleurs menstruelles')),
        ('Retard de règles', _('Retard de règles')),
        ('Suivi de grossesse', _('Suivi de grossesse')),
        ('Contraception', _('Contraception')),

        # Gériatrie
        ('Chutes répétées', _('Chutes répétées')),
        ('Diminution de mémoire', _('Diminution de mémoire')),
        ('Douleurs chroniques', _('Douleurs chroniques')),
    ]

    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='consultations',
        verbose_name=_("Patient")
    )

    medecin = models.ForeignKey(
        'Personnel',
        on_delete=models.CASCADE,
        related_name='consultations',
        limit_choices_to={'role': 'Médecin'},
        verbose_name=_("Médecin")
    )
    
    infirmier = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations_as_nurse',
        verbose_name=_("Infirmier")
    )

    date_consultation = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date de la consultation")
    )

    # ✅ CORRECTION : CharField au lieu de TextField + choix valides
    type_consultation = models.CharField(
        max_length=50,
        choices=TYPE_CONSULTATION_CHOICES,
        default='Première consultation',
        verbose_name=_("Type de consultation"),
        help_text=_("Choisissez le motif ou le type de consultation.")
    )

    motif = models.CharField(
        max_length=200,
        verbose_name=_("Motif"),
        help_text=_("Motif principal de la consultation.")
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Symptômes ou situation rapportée.")
    )

    poids = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Poids (kg)")
    )

    taille = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Taille (cm)")
    )

    tension_artérielle = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name=_("Tension artérielle"),
        help_text="Ex: 12/8"
    )

    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        blank=True, null=True,
        verbose_name=_("Température (°C)")
    )

    pouls = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Pouls (bpm)")
    )

    diagnostic = models.TextField(
        blank=True, null=True,
        verbose_name=_("Diagnostic"),
        help_text=_("Diagnostic établi lors de la consultation.")
    )

    traitement = models.TextField(
        blank=True, null=True,
        verbose_name=_("Traitement prescrit"),
        help_text=_("Le traitement prescrit au patient.")
    )

    note = models.TextField(
        blank=True, null=True,
        verbose_name=_("Note complémentaire"),
        help_text=_("Informations additionnelles.")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Planifiée',
        verbose_name=_("Statut")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation du {self.date_consultation.strftime('%d/%m/%Y')} - {self.patient}"

    class Meta:
        verbose_name = _("Consultation")
        verbose_name_plural = _("Consultations")
        ordering = ['-date_consultation']

    def get_montant_du(self):
        """
        Retourne le montant dû pour cette consultation selon son type.
        """
        prices = {
            'Première consultation': Decimal('1000.00'),
            'Suivi': Decimal('3000.00'),
            'Urgence': Decimal('7000.00'),
            'Téléconsultation': Decimal('4000.00'),
        }
        return prices.get(self.type_consultation, Decimal('1000.00'))

#
#
#
# class Paiement(models.Model):
#     """
#     Informations sur le paiement d'une consultation.
#     """
#     TYPE_CHOICES = [
#         ('Espèces', _('Espèces')),
#         ('Carte Bancaire', _('Carte Bancaire')),
#         ('Mobile Money', _('Mobile Money')),
#     ]

#     consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE)
#     montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
#     type_paiement = models.CharField(max_length=20, choices=TYPE_CHOICES)
#     date_paiement = models.DateTimeField(auto_now_add=True)

#     @staticmethod
#     def total_payments_for_patient(patient):
#         return Paiement.objects.filter(consultation__patient=patient).aggregate(total=models.Sum('montant'))['total'] or 0

#     def __str__(self):
#         return f"Paiement de {self.montant} par {self.consultation.patient} - {self.type_paiement}"

#     class Meta:
#         verbose_name = _("Paiement")
#         verbose_name_plural = _("Paiements")
#
#
#


class Medicament(models.Model):
    """
    Représente un médicament en stock.
    """
    nom = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def is_in_stock(self, quantity):
        return self.stock >= quantity

    def __str__(self):
        return f"{self.nom} - {self.stock} en stock"

    class Meta:
        verbose_name = _("Médicament")
        verbose_name_plural = _("Médicaments")





class Examen(models.Model):
    """
    Examens médicaux demandés ou réalisés pendant une consultation.
    Le patient est récupéré via la consultation, pas via une ForeignKey directe.
    """
    STATUT_CHOICES = [
        ('En attente', _('En attente')),
        ('Réaliser', _('Réaliser')),
    ]

    nom = models.CharField(_('Nom de l’examen'), max_length=100)
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        verbose_name=_('Consultation')
    )
    date_examen = models.DateField(
        _('Date de l’examen'),
        auto_now_add=True,  # ✅ Date automatique à la création
        null=False,
        blank=False
    )
    resultat = models.TextField(_('Résultat'), blank=True, null=True)
    cout = models.DecimalField(
        _('Coût de l’examen'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True
    )
    statut = models.CharField(
        _('Statut'),
        max_length=15,
        choices=STATUT_CHOICES,
        default='En attente'
    )

    def mark_as_completed(self, result=None):
        """
        Marque l’examen comme réalisé avec un résultat optionnel.
        """
        self.statut = 'Réaliser'
        if result is not None:
            self.resultat = result
        self.save(update_fields=['statut', 'resultat'])

    def get_patient(self):
        """
        Récupère le patient via la consultation
        """
        return self.consultation.patient if self.consultation else None

    def __str__(self):
        return f"Examen {self.nom} - Statut: {self.get_statut_display() or self.statut} - Patient: {self.get_patient() or 'Aucun'}"

    
    def get_cout(self):
        """
        Returns the total cost of the prescribed medication as a Decimal.
        """
        # Example: sum the cost of all medications in the ordonnance
        total = Decimal('0.00')
        # Assuming you have a related field 'medicaments' with cost attribute
        
        return total
    class Meta:
        verbose_name = _("Examen")
        verbose_name_plural = _("Examens")
        
    
  


class Ordonnance(models.Model):
    """
    Ordonnance prescrite suite à une consultation.
    """
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)

    @property
    def patient(self):
        return self.consultation.patient

    nom_medicament = models.CharField(max_length=100, verbose_name=_("Nom du médicament"))
    posologie = models.TextField(verbose_name=_("Posologie"))
    duree = models.CharField(max_length=50, verbose_name=_("Durée du traitement"))
    quantite = models.PositiveIntegerField(verbose_name=_("Quantité prescrite"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes supplémentaires"))
    date_prescription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ordonnance du {self.date_prescription.strftime('%d/%m/%Y')} - {self.patient} - {self.nom_medicament}"

    class Meta:
        verbose_name = _("Ordonnance")
        verbose_name_plural = _("Ordonnances")
        ordering = ['-date_prescription']
        
    def get_cout(self):
        """
        Return the cost as a Decimal to avoid type errors.
        """
        
        return Decimal('0.00')

class RendezVous(models.Model):
    STATUS_CHOICES = [
        ('En attente', _('En attente')),
        ('Confirmé', _('Confirmé')),
        ('Annulé', _('Annulé')),
        ('Terminé', _('Terminé')),
    ]

    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        related_name='rendezvous_list',
        verbose_name=_("Patient")
    )

    medecin = models.ForeignKey(
        'Personnel',
        on_delete=models.CASCADE,
        related_name='rendezvous_list',
        limit_choices_to={'role': 'Médecin'},
        verbose_name=_("Médecin")
    )

    date_rendezvous = models.DateField(
        _("Date du rendez-vous"),
        help_text=_("Sélectionnez une date.")
    )

    heure_debut = models.TimeField(
        _("Heure de début"),
        help_text=_("Exemple: 09:30")
    )

    heure_fin = models.TimeField(
        _("Heure de fin"),
        help_text=_("Exemple: 10:00")
    )

    motif = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Motif du rendez-vous"),
        help_text=_("Raison du rendez-vous (facultatif).")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='En attente',
        verbose_name=_("Statut")
    )

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Consultation")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rendez-vous du {self.date_rendezvous} à {self.heure_debut} - {self.patient}"

    class Meta:
        verbose_name = _("Rendez-vous")
        verbose_name_plural = _("Rendez-vous")
        ordering = ['-date_rendezvous', '-heure_debut']
    
    def get_cout(self):
        # Calculate the total cost of all medications in the prescription
        return sum(medicament.prix for medicament in self.medicaments.all())
        
        


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        


from decimal import Decimal
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

# === MODES DE PAIEMENT ===
TYPE_PAIEMENT_CHOICES = [
    ('Espèces', _('Espèces')),
    ('Carte Bancaire', _('Carte Bancaire (Visa/MasterCard)')),
    ('Mobile Money', _('Mobile Money')),
    ('Airtel Money', _('Airtel Money')),
    ('OnyFast', _('OnyFast')),
    ('Virement', _('Virement bancaire')),
    ('Assurance', _('Paiement par assurance')),
    ('Autre', _('Autre')),
]

# === STATUT DU PAIEMENT ===
STATUS_PAIEMENT_CHOICES = [
    ('Payé', _('Payé')),
    ('Partiellement payé', _('Partiellement payé')),
    ('Non payé', _('Non payé')),
    ('Remboursé', _('Remboursé')),
    ('Annulé', _('Annulé')),
]

# models.py

class Paiement(models.Model):
    """
    Enregistre chaque paiement effectué par un patient.
    Peut être lié à une consultation, un examen ou une ordonnance.
    """
    consultation = models.ForeignKey(
        'Consultation',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Consultation")
    )
    examen = models.ForeignKey(
        'Examen',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Examen")
    )
    ordonnance = models.ForeignKey(
        'Ordonnance',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Ordonnance")
    )

    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Montant total dû")
    )
    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Montant payé")
    )
    difference_rendue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Différence rendue")
    )
    type_paiement = models.CharField(
        max_length=30,
        choices=TYPE_PAIEMENT_CHOICES,
        default='Espèces',
        verbose_name=_("Mode de paiement")
    )
    numero_transaction = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Numéro de transaction")
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_PAIEMENT_CHOICES,
        default='Non payé',
        verbose_name=_("Statut du paiement")
    )
    personnel = models.ForeignKey(
        'Personnel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Utilisateur qui a enregistré le paiement")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes supplémentaires")
    )
    date_paiement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.montant_paye} XAF - {self.get_type_paiement_display()}"

    def get_montant_du(self):
        """Retourne le montant total dû selon l'acte médical"""
        montant_du = Decimal('0.00')
        if self.consultation:
            montant_du += self.consultation.get_montant_du()
        if self.examen:
            montant_du += self.examen.get_cout()
        if self.ordonnance:
            montant_du += self.ordonnance.get_cout()
        return montant_du

    def update_status(self):
        montant_paye = self.montant_paye
        montant_total = self.montant_total
        if montant_paye >= montant_total:
            self.status = 'Payé'
        elif montant_paye > Decimal('0.00'):
            self.status = 'Partiellement payé'
        else:
            self.status = 'Non payé'
        self.save(update_fields=['status'])

    def calculer_difference(self):
        if self.montant_paye > self.montant_total:
            self.difference_rendue = self.montant_paye - self.montant_total
        else:
            self.difference_rendue = Decimal('0.00')
        self.save(update_fields=['difference_rendue'])

    class Meta:
        ordering = ['-date_paiement']