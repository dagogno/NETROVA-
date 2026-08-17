from django.apps import AppConfig


class MembresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'membres'
    verbose_name = 'Membres'

    def ready(self):
        import membres.signals  # noqa — charge les signaux au démarrage
