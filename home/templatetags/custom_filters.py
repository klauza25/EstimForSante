# home/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def filter_non_terminees(consultations):
    """
    Filtre les consultations qui ne sont pas terminées.
    """
    if hasattr(consultations, 'all'):
        # Si c'est un QuerySet
        return consultations.filter(status__in=['Planifiée', 'En cours'])
    else:
        # Si c'est une liste
        return [c for c in consultations if c.status in ['Planifiée', 'En cours']]