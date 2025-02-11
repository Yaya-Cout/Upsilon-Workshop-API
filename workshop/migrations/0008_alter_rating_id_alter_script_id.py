# Created by hand

from django.db import migrations, models
import uuid

class Char36UUIDField(models.UUIDField):
    def db_type(self, connection):
        return "char(36)"

class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0007_alter_rating_id_alter_script_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='id',
            field=Char36UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='script',
            name='id',
            field=Char36UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='UUID'),
        ),
    ]
