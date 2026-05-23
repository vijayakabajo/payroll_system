from django.apps import AppConfig


class ConfigsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.configs'
    label = 'configs'
    verbose_name = 'Configuration'
