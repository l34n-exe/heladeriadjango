from django.apps import AppConfig

class HeladeriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'heladeria'

    def ready(self):
        import heladeria.signals  