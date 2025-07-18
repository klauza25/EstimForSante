from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from home.views import User

User = get_user_model()

# class Presence(models.Model):
#     ROLES = [
#         ("medecin", "Médecin"),
#         ("infirmier", "Infirmier"),
#         ("pharmacien", "Pharmacien"),
#         ("accueil", "Accueil"),
#     ]

#     employe = models.ForeignKey(User, on_delete=models.CASCADE)
#     arrivee = models.DateTimeField(null=True, blank=True)  # Stocke l'heure d'arrivée
#     depart = models.DateTimeField(null=True, blank=True)  # Stocke l'heure de départ
#     role = models.CharField(max_length=20, choices=ROLES)

#     def __str__(self):
#         return f"{self.employe.username} - {self.arrivee.date() if self.arrivee else 'Non pointé'}"




class Presence(models.Model):
    ROLES = [
        ("medecin", "Médecin"),
        ("infirmier", "Infirmier"),
        ("pharmacien", "Pharmacien"),
        ("accueil", "Accueil"),
    ]

    employe = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)  # Rôle du personnel
    arrivee = models.DateTimeField(default=now)  # Heure d'arrivée
    depart = models.DateTimeField(null=True, blank=True)  # Heure de départ

    def __str__(self):
        return f"{self.employe.username} ({self.role}) - {self.arrivee.strftime('%Y-%m-%d %H:%M:%S')}"
        class Meta :
                db_table = "presence"