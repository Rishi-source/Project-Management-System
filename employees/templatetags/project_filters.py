from django import template

register = template.Library()

@register.filter(name='get_value')
def get_value(recent_physical_progress, project_id):
    return recent_physical_progress.get(project_id, 0)
