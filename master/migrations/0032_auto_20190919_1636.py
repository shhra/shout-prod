# Generated by Django 2.2.3 on 2019-09-19 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0031_auto_20190910_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, default=None, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, default=None, max_length=1, null=True),
        ),
    ]