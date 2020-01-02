from django.apps import AppConfig

class AuthenticationAppConfig(AppConfig):
    name = 'shout_app.authentication'
    label = 'authentication'
    verbose_name = 'Authentication'

    def ready(self):
        import shout_app.authentication.signals

default_app_config = 'shout_app.authentication.AuthenticationAppConfig'

