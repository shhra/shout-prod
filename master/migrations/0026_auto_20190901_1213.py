# Generated by Django 2.2.3 on 2019-09-01 12:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0025_auto_20190901_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='slug',
            field=models.SlugField(default=uuid.uuid4, editable=False, max_length=80, unique=True),
        ),
        migrations.AlterField(
            model_name='shout',
            name='slug',
            field=models.SlugField(default=uuid.uuid4, editable=False, max_length=80, unique=True),
        ),
    ]
