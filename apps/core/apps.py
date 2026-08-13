from django.apps import AppConfig
import logging
logger = logging.getLogger(__name__)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    _observer = None

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') or not os.environ.get('DJANGO_AUTORELOAD'):
            try:
                from apps.knowledge.watcher import start_watchdog
                self._observer = start_watchdog()
                logger.info("Knowledge Watchdog started.")
            except Exception as e:
                logger.error(f"Failed to start watchdog: {e}")