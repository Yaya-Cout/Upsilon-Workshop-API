# Generated by Django 4.1.5 on 2023-01-10 17:31

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import workshop.api.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OS",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("url", models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Script",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "files",
                    models.JSONField(
                        validators=[workshop.api.validators.validate_script_files]
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "language",
                    models.CharField(
                        max_length=100,
                        validators=[workshop.api.validators.validate_language],
                    ),
                ),
                ("version", models.CharField(default="1.0", max_length=100)),
                ("description", models.TextField(blank=True)),
                ("views", models.IntegerField(default=0)),
                ("licence", models.CharField(default="MIT", max_length=100)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scripts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("compatibility", models.ManyToManyField(blank=True, to="workshop.os")),
            ],
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "script",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ratings",
                        to="workshop.script",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ratings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]