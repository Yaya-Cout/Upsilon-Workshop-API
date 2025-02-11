# Generated by Django 4.2.18 on 2025-02-11 13:49

from django.db import migrations
import uuid
import workshop.api.models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0008_alter_rating_id_alter_script_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='id',
            field=workshop.api.models.RealUUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='script',
            name='id',
            field=workshop.api.models.RealUUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID'),
        ),
    ]
