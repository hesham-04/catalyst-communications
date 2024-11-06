# projects/templatetags/project_tags.py

from django import template

register = template.Library()

@register.filter
def status_badge_color(status):
    return {
        'QT': 'primary',
        'AW': 'warning',
        'CL': 'danger',
        'IP': 'info',
        'FN': 'success',
    }.get(status, 'secondary')

@register.filter
def status_text_color(status):
    return {
        'QT': 'primary',
        'AW': 'warning',
        'CL': 'danger',
        'IP': 'info',
        'FN': 'success',
    }.get(status, 'secondary')
