from django.conf import settings


def company_context(request):
    """Inject company info into every template context."""
    return {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'Minu Marketing Pvt Ltd'),
        'COMPANY_TAGLINE': getattr(settings, 'COMPANY_TAGLINE', 'Growing Together'),
    }
