
import os
from requests import get

from django.db import migrations


def add_encodings(apps, schema_editor):
    url = os.getenv('ENC_URL') + '/encode'
    Shout = apps.get_model('shouts', 'Shout')
    for shout in Shout.objects.all().filter(value=None):
        encoded_content = get(url=url, json={'shout': shout.body})
        shout.value = encoded_content.json()['encodings']
        shout.save()


class Migration(migrations.Migration):

    dependencies = [
        ('shouts', '0003_shout_value'),
    ]

    operations = [
        migrations.RunPython(add_encodings)
    ]
