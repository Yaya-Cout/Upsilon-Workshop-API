"""Custom validators for Upsilon workshop models."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_LANGUAGES = [
    'python',
    'micropython-khicas',
    'xcas-python-**',
    'xcas-python-xor',
    'xcas',
    'xcas-session'
]


def validate_language(value):
    """Validate the language of a script."""
    if value not in ALLOWED_LANGUAGES:
        raise ValidationError(
            _('%(value)s is not a valid language'),
            params={'value': value},
        )
