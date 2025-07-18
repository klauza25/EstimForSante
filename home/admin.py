from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import User, Patient, Personnel, Consultation, Examen, Paiement, Medicament, Ordonnance, RendezVous

# Personnalisation du titre et de l'en-tête de l'interface admin
admin.site.site_title = _("E-SANTÉ")
admin.site.site_header = _("E-SANTÉ ADMIN")
admin.site.index_title = _("Tableau de bord administratif")

# === ADMIN POUR USER ===
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Administration personnalisée pour le modèle utilisateur.
    """
    list_display = ('username', 'email', 'is_staff', 'get_role')
    fieldsets = UserAdmin.fieldsets + (
        (_("Rôles"), {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("Rôles"), {'fields': ('role',)}),
    )

    def get_role(self, obj):
        return obj.get_role_display()
    get_role.short_description = _("Rôle")

# === ADMIN POUR PATIENT ===
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'date_naissance', 'telephone', 'email')
    search_fields = ('nom', 'prenom', 'email')
    list_filter = ('date_naissance',)
    ordering = ('nom', 'prenom')

# === ADMIN POUR PERSONNEL ===
@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'role', 'specialite', 'telephone', 'email', 'user')
    search_fields = ('nom', 'prenom', 'role', 'email')
    list_filter = ('role', 'specialite')
    ordering = ('nom', 'prenom')

# === ADMIN POUR CONSULTATION ===
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_consultation', 'status', 'motif')
    search_fields = ('patient__nom', 'patient__prenom', 'medecin__nom', 'medecin__prenom')
    list_filter = ('status', 'date_consultation', 'medecin')
    ordering = ['-date_consultation']

    def marquer_comme_terminee(self, request, queryset):
        queryset.update(status='Terminée')
    marquer_comme_terminee.short_description = _("Marquer les consultations sélectionnées comme terminées")

    actions = [marquer_comme_terminee]

# === ADMIN POUR EXAMEN ===
@admin.action(description=_("Marquer les examens comme réalisés"))
def marquer_comme_realises(modeladmin, request, queryset):
    queryset.update(statut="Réalisé")

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('nom', 'consultation', 'date_examen', 'statut')
    search_fields = ('nom', 'consultation__patient__nom')
    list_filter = ('statut',)
    ordering = ('date_examen',)
    actions = [marquer_comme_realises]

# === ADMIN POUR PAIEMENT ===
# admin.py


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        'consultation',
        'montant_total',
        'montant_paye',
        'type_paiement',
        'difference_rendue',
        'status',
        'date_paiement',
        'get_patient'
    )
    search_fields = ('consultation__patient__nom', 'numero_transaction')
    list_filter = ('type_paiement', 'status', 'date_paiement')
    readonly_fields = ('date_paiement', 'montant_total')

    def get_patient(self, obj):
        return obj.consultation.patient if obj.consultation else "—"
    get_patient.short_description = _("Patient")
    get_patient.admin_order_field = 'consultation__patient'

# === ADMIN POUR MÉDICAMENT ===
@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'stock', 'prix')
    search_fields = ('nom',)
    list_filter = ('stock',)
    ordering = ('nom',)

# === ADMIN POUR ORDONNANCE ===
@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'date_ordonnance', 'liste_medicaments', 'quantite')
    search_fields = ('consultation__patient__nom', 'medicament__nom')
    list_filter = ('consultation__date_consultation',)
    ordering = ('-consultation__date_consultation',)

    def date_ordonnance(self, obj):
        return obj.consultation.date_consultation
    date_ordonnance.short_description = _("Date de l'ordonnance")

    def liste_medicaments(self, obj):
        return ", ".join([str(m) for m in obj.medicaments.all()])
    liste_medicaments.short_description = _("Médicaments")

# === ADMIN POUR RENDEZ-VOUS ===
@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_rendezvous', 'heure_debut', 'heure_fin', 'status')
    list_filter = ('status', 'date_rendezvous', 'medecin')
    search_fields = ('patient__nom', 'medecin__nom', 'motif')
    ordering = ('date_rendezvous', 'heure_debut')