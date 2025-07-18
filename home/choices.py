# choices.py
from django.utils.translation import gettext_lazy as _

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