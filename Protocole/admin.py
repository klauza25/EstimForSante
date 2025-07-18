from django.contrib import admin
from .models import Presence

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("employe", "role", "arrivee", "depart")
    list_filter = ("role", "arrivee", "depart")