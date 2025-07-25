from django.urls import path
from . import views
from django.conf.urls import handler404
from home.views import handler404_view

handler404 = 'home.views.handler404_view'


urlpatterns = [
    # === Accueil & Auth ===
    path('', views.home, name='home'),
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),  # Si tu as ta propre vue de logout
    # === Dashboard par rôle ===
    path('dashboard/docteur/', views.dashboard_docteur, name='dashboard_docteur'),
    path('dashboard/infirmier/', views.dashboard_infirmier, name='dashboard_infirmier'),
    path('dashboard/accueil/', views.dashboard_accueil, name='dashboard_accueil'),
    path('dashboard/pharmacien/', views.dashboard_pharmacien, name='dashboard_pharmacien'),  # À vérifier
    # === Patients ===
    path('patients/', views.liste_patients, name='liste_patients'),
    path('patients/<int:patient_id>/modifier/', views.modifier_patient, name='modifier_patient'),
    path('patients/<int:patient_id>/supprimer/', views.supprimer_patient, name='supprimer_patient'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('assignation-consultation/', views.assignation_consultation, name='assignation_consultation'),
    path('patients/ajouter/', views.ajouter_patient, name='ajouter_patient'),
    path('reassignation/', views.reassignation_consultation, name='reassignation_consultation'),    # === Consultations ===
    path('consultations/', views.consultations, name='liste_consultations'),
    path('consultations/nouvelle/', views.create_consultation, name='create_consultation'),
    path('consultations/<int:consultation_id>/', views.consultation_detail, name='consultation_detail'),
    path('consultations/<int:consultation_id>/modifier/', views.update_consultation, name='update_consultation'),
    path('consultations/gestion/', views.manage_consultations, name='manage_consultations'),
    path('consultations/<int:consultation_id>/modifier/', views.update_consultation, name='modifier_consultation'),
    path('consultations/<int:consultation_id>/supprimer/', views.delete_consultation, name='supprimer_consultation'),
    path('consultations/<int:consultation_id>/examen/ajouter/', views.ajouter_examen, name='ajouter_examen'),
    path('consultations/<int:consultation_id>/rendezvous/ajouter/', views.create_rendezvous, name='create_rendezvous'),
    path('rendezvous/<int:rendezvous_id>/', views.rendezvous_detail, name='rendezvous_detail'),  # Optional detail view
    path('rendezvous/', views.liste_rendezvous, name='liste_rendezvous'),

    # === Examens ===
    path('examens/', views.liste_examens, name='liste_examens'),
    path('examens/<int:examen_id>/valider/', views.valider_examen, name='valider_examen'),
    path('examens/ajouter/', views.ajouter_examen, name='ajouter_examen'),
    # === Ordonnances ===  
    path('ordonnances/', views.liste_ordonnances, name='liste_ordonnances'),
    path('ordonnances/patient/<int:patient_id>/', views.liste_ordonnances, name='ordonnances_patient'),
    path('ordonnances/nouvelle/<int:consultation_id>/', views.creer_ordonnance, name='creer_ordonnance'),
    path('ordonnances/<int:id>/', views.detail_ordonnance, name='detail_ordonnance'),
    path('api/rechercher-medicament/', views.rechercher_medicament, name='rechercher_medicament'),
    path('api/drugs/search/<str:term>/', views.search_drug, name='search_drug'),
    path('api/drugs/info/<str:drug_name>/', views.get_drug_info, name='get_drug_info'),
   # === Personnel ===
    path('personnel/', views.personnel_list, name='liste_personnel'),
    path('personnel/<int:pk>/', views.personnel_detail, name='personnel_detail'),
     path('utilisateurs-en-ligne/', views.users_online, name='users_online'),
    path('gestion-utilisateurs/', views.manage_connected_users, name='manage_connected_users'),
    
    path('historique-clinique/', views.historique_clinique, name='historique_clinique'),
    path('paiement/ajouter/<int:consultation_id>/', views.enregistrer_paiement, name='enregistrer_paiement_consultation'),
    path('paiements/', views.liste_paiements, name='liste_paiements'),
    path('caisse/', views.caisse, name='caisse'),
    path('paiement/<int:paiement_id>/imprimer/', views.generate_pdf, name='imprimer_facture'),
    path('paiement/<int:pk>/', views.detail_paiement, name='detail_paiement'),
    path('mes-consultations/', views.mes_consultations, name='mes_consultations'),
    path('assignation/consultation/', views.assignation_consultation, name='assignation_consultation'),
    path('assignation/consultation/<int:consultation_id>/modifier/', views.modifier_assignation, name='modifier_assignation'),
    path('assignation/consultation/<int:consultation_id>/supprimer/', views.supprimer_assignation, name='supprimer_assignation'),

]