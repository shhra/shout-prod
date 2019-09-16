# Generated by Django 2.2.3 on 2019-08-30 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('master', '0014_auto_20190814_0529'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advice',
            name='professional',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Professional',
        ),
    ]
