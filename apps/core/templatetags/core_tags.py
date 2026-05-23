from django import template
from apps.core.utils import format_indian_currency, amount_in_words

register = template.Library()


@register.filter
def currency(value):
    """Format value as Indian currency: ₹1,25,000.00"""
    return format_indian_currency(value)


@register.filter
def in_words(value):
    """Convert number to Indian English words."""
    return amount_in_words(value)


@register.filter
def status_badge_class(status):
    """Return CSS class for a status string."""
    mapping = {
        'generated': 'badge-success',
        'pending': 'badge-warning',
        'failed': 'badge-danger',
        'processing': 'badge-info',
        'completed': 'badge-success',
        'partial': 'badge-warning',
        'sent': 'badge-success',
        'not_sent': 'badge-secondary',
    }
    return mapping.get(str(status).lower(), 'badge-secondary')


@register.filter
def status_label(status):
    """Return human-readable label for a status."""
    mapping = {
        'generated': 'Generated',
        'pending': 'Pending',
        'failed': 'Failed',
        'processing': 'Processing',
        'completed': 'Completed',
        'partial': 'Partial',
        'sent': 'Sent',
        'not_sent': 'Not Sent',
    }
    return mapping.get(str(status).lower(), status.replace('_', ' ').title())


@register.simple_tag
def active_nav(request, url_name):
    """Return 'active' class if the current URL matches the given name."""
    from django.urls import reverse
    try:
        if request.path.startswith(reverse(url_name)):
            return 'active'
    except Exception:
        pass
    return ''
