# Generated by Django 2.2 on 2020-01-10 04:30

from django.db import migrations

from django.conf import settings


def update_site_name(apps, schema_editor):
    SiteModel = apps.get_model('sites', 'Site')
    domain = 'apprester.com'
    name = 'ShoutIt'

    SiteModel.objects.update_or_create(
        pk=settings.SITE_ID,
        domain=domain,
        name=name
    )


class Migration(migrations.Migration):

    dependencies = [
        # Make sure the dependency that was here by default is also included here
        ('sites', '0002_alter_domain_unique'), # Required to reference `sites` in `apps.get_model()`
    ]

    operations = [
        migrations.RunPython(update_site_name),
    ]
