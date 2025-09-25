from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolio"
    
    def ready(self):
        """Import signals and admin configurations when the app is ready."""
        import portfolio.profile  # This will register the signals
        import portfolio.profile_admin  # This will register the admin
