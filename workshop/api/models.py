"""Database models for the Upsilon Workshop app."""
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

# Import the User and Group models from the Django auth module
from django.contrib.auth.models import AbstractUser

# Import uuid to generate unique IDs
import uuid

# Import the validators from the validators.py file
from workshop.api.validators import validate_language, validate_email, validate_runner, validate_script_files, URLUsernameValidator

# Max file size is 100 KB
MAX_FILE_SIZE = 100 * 1024


class User(AbstractUser):
    """User model."""

    # The email address of the user
    email = models.EmailField(
        _("email address"),
        validators=[validate_email]
    )

    # Remove the id field
    id = None

    # Field to store whether to warn user about the existence of the private
    # projects
    warning_private_project = models.BooleanField(
        default=False,
        help_text="This field specify wether the user should be informed about"
                  " the existence of the private projects"
    )

    # The username is the primary key
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        primary_key=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/+/-/_ only."
        ),
        validators=[URLUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.username}"


class UUIDModel(models.Model):
    """Abstract model that uses UUIDs as primary keys."""

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,
                          primary_key=True, verbose_name='UUID')

    class Meta:
        """Meta class for the UUIDModel."""

        abstract = True


class Rating(UUIDModel):
    """Model for the rating of a script."""

    # The rating is a number between 0 and 5
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    # The comment is an optional text field that can be used to explain the
    # rating
    comment = models.TextField(blank=True)

    # The created and modified fields are automatically set by Django
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # The user that created the rating
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    # The script that was rated
    script = models.ForeignKey(
        'Script',
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return str(self.rating)


class OS(models.Model):
    """Operating system model."""

    # The name of the operating system
    name = models.CharField(max_length=100, primary_key=True, unique=True)

    # The description of the operating system
    description = models.TextField(blank=True)

    # The URL of the operating system
    homepage = models.URLField(blank=True)

    # TODO: Add a version field
    # TODO: Add a icon field

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.name}"


class Tag(models.Model):
    """Tag model."""

    # The name of the tag
    name = models.CharField(max_length=100, primary_key=True, unique=True)

    # The description of the tag
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.name}"


class Script(UUIDModel):
    """A script stored in the database.

    Scripts are stored in the database as a string of text.
    They have metadata associated with them:
    - The name of the script
    - The author of the script
    - The date the script was created
    - The date the script was last modified
    - The language the script is written in
    - The version of the script
    - The short description of the script
    - The long description of the script
    - The comments on the script
    - The number of times the script has been downloaded
    - The number of times the script has been viewed
    - The content of the script
    - The licence of the script
    - The compatibility of the script
    - and more...
    """

    # The files that are used in the script
    files = models.JSONField(
        validators=[validate_script_files]
    )

    # The name of the script
    # TODO: Forbid multiple scripts with the same name for the same user, but
    # allow multiple scripts with the same name for different users
    name = models.CharField(max_length=100)

    # The author of the script (user is keept when the script is deleted,
    # but the script is deleted when the user is deleted)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scripts'
    )

    # Collaborators of the script (should be displayed along with the author,
    # have read/write access to the script, but can't delete the script)
    collaborators = models.ManyToManyField(
        User,
        related_name='collaborations',
        blank=True
    )

    # The date the script was created
    created = models.DateTimeField(auto_now_add=True)

    # The date the script was last modified
    modified = models.DateTimeField(auto_now=True)

    # The language the script is written in (listed in
    # ALLOWED_LANGUAGES in validators.py)
    language = models.CharField(max_length=100, validators=[validate_language])

    # The version of the script
    version = models.CharField(max_length=100, default='1.0')

    # The short description of the script
    short_description = models.TextField(blank=True, max_length=100)

    # The long description of the script
    long_description = models.TextField(blank=True, max_length=10000)

    # The number of times the script has been downloaded
    # downloads = models.IntegerField(default=0)

    # The number of times the script has been viewed
    views = models.IntegerField(default=0)

    # The licence of the script
    licence = models.CharField(max_length=100, default='Unspecified')

    # The compatibility of the script
    # TODO: Forbid empty values
    compatibility = models.ManyToManyField(OS, blank=True)

    # The tags of the script
    tags = models.ManyToManyField(Tag, blank=True)

    # The visibility of the script
    is_public = models.BooleanField(default=True)

    # The simulator to run the project with (possible values : default (Upsilon),
    # parisse-with-xcas)
    runner = models.CharField(
        max_length=100, default='default', validators=[validate_runner]
    )

    # TODO: Add a field for compatibles machines
    # TODO: Add a field for size of the script
