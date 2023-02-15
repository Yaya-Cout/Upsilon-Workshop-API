"""Custom validators for Upsilon workshop models."""
import json

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_LANGUAGES = [
    'python',
    'micropython-khicas',
    'xcas-python-pow',
    'xcas-python-xor',
    'xcas',
    'xcas-session'
]

# Max script size is 100 KB
MAX_SCRIPT_SIZE = 100 * 1024


def validate_language(value):
    """Validate the language of a script."""
    if value not in ALLOWED_LANGUAGES:
        raise ValidationError(
            _('%(value)s is not a valid language'),
            params={'value': value},
        )


def validate_email(value):
    """Validate the email of a user."""
    if '@' not in value:
        raise ValidationError(
            _('%(value)s is not a valid email address'),
            params={'value': value},
        )


def validate_script_files(value):
    """Validate the script file."""
    # Check file size
    if len(json.dumps(value)) > MAX_SCRIPT_SIZE:
        raise ValidationError(
            _('The file is too large (%(size)s bytes). '
              'The maximum file size is %(max_size)s bytes.'),
            params={'size': len(str(value)), 'max_size': MAX_SCRIPT_SIZE},
        )

    # Check JSON format
    # Example of a valid JSON file:
    # [
    #     {
    #         "name": "file1.py",
    #         "content": "print('Hello world!')"
    #     },
    #     {
    #         "name": "file2.py",
    #         "content": "import file1"
    #     }
    # ]
    # Check that there are files in the JSON file
    if len(value) == 0:
        raise ValidationError(
            _('The file is empty.'),
        )
    # Check that the format is correct (no missing or extra fields)
    for file in value:
        # Ensure that content and name are present
        if 'name' not in file:
            raise ValidationError(
                _('The file is not a valid JSON file.'
                  'The field "name" is missing.'),
            )
        if 'content' not in file:
            raise ValidationError(
                _('The file is not a valid JSON file.'
                  'The field "content" is missing on file %(name)s.'),
                params={'name': file['name']},
            )

        # Ensure that there are no extra fields
        if len(file) != 2:
            raise ValidationError(
                _('The file is not a valid JSON file.'
                  'The file %(name)s has extra fields.'),
                params={'name': file['name']},
            )

        # Check that file name is valid (has extension and does not contain any
        # slash)
        if '.' not in file['name']:
            raise ValidationError(
                _('The file is not a valid JSON file.'
                  'The file %(name)s has no extension.'),
                params={'name': file['name']},
            )

        if '/' in file['name']:
            raise ValidationError(
                _('The file is not a valid JSON file.'
                  'The file %(name)s contains a slash.'),
                params={'name': file['name']},
            )

    # Check that the file names are unique
    names = [file['name'] for file in value]
    if len(names) != len(set(names)):
        raise ValidationError(
            _('The file is not a valid JSON file.'
              'The file names are not unique.'),
        )
