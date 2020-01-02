from django.apps import AppConfig

class ShoutsAppConfig(AppConfig):
    name = 'shout_app.shouts'
    label = 'shouts'
    verbose_name='Shouts'

    def ready(self):
        import shout_app.shouts.signals

default_app_config = 'shout_app.shouts.ShoutsAppConfig'

