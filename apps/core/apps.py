from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        # Placeholder for Watchdog initialization (will be added in Sprint 2)
        # We'll start the watchdog here later.
        logger.info("Core app ready. Resource monitor available.")