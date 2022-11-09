"""Database models for the Upsilon Workshop app."""
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Import the User and Group models from the Django auth module
from django.contrib.auth.models import User, Group

# Import the validators from the validators.py file
from workshop.quickstart.validators import validate_language

# Models are the objects that are stored in the database

class Rating(models.Model):
    """Model for the rating of a script."""

    # The rating is a number between 0 and 5
    rating = models.IntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(5)]
    )

    # The comment is an optional text field that can be used to explain the
    # rating
    comment = models.TextField(blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return str(self.rating)



class OS(models.Model):
    """Operating system model."""

    # The name of the operating system
    name = models.CharField(max_length=100)

    # TODO: Add a version field

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.name}"

class Script(models.Model):
    """A script stored in the database.

    Scripts are stored in the database as a string of text.
    They have metadata associated with them:
    - The name of the script
    - The author of the script (using relations)
    - The date the script was created
    - The date the script was last modified
    - The language the script is written in
    - The version of the script
    - The description of the script
    - The rating of the script
    - The comments on the script
    - The number of times the script has been downloaded
    - The number of times the script has been viewed
    - The content of the script
    - The licence of the script
    - The compatibility of the script
    - and more...
    """

    # The content of the script
    content = models.TextField()

    # The name of the script (must be unique)
    name = models.CharField(max_length=100, unique=True)

    # The author of the script (user is keept when the script is deleted,
    # but the script is deleted when the user is deleted)
    authors = models.ManyToManyField(User)

    # The date the script was created
    created = models.DateTimeField(auto_now_add=True)

    # The date the script was last modified
    modified = models.DateTimeField(auto_now=True)

    # The language the script is written in (listed in
    # ALLOWED_LANGUAGES in validators.py)
    language = models.CharField(max_length=100, validators=[validate_language])

    # The version of the script
    version = models.CharField(max_length=100, default='1.0')

    # The description of the script
    description = models.TextField(blank=True)

    # The ratings of the script
    ratings = models.ManyToManyField(Rating, blank=True)

    # The number of times the script has been downloaded
    downloads = models.IntegerField(default=0)

    # The number of times the script has been viewed
    views = models.IntegerField(default=0)

    # The licence of the script
    licence = models.CharField(max_length=100, default='MIT')

    # The compatibility of the script
    compatibility = models.ManyToManyField(OS)
