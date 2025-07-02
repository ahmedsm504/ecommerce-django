from django.apps import AppConfig


# store/apps.py

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signals  # هذا السطر ضروري لتشغيل الكود
