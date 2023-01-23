# Generated by Django 4.1.5 on 2023-01-23 17:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("workshop", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="os",
            old_name="url",
            new_name="homepage",
        ),
        migrations.RemoveField(
            model_name="os",
            name="id",
        ),
        migrations.AlterField(
            model_name="os",
            name="name",
            field=models.CharField(
                max_length=100, primary_key=True, serialize=False, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="rating",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
                verbose_name="UUID",
            ),
        ),
        migrations.AlterField(
            model_name="script",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
                verbose_name="UUID",
            ),
        ),
    ]