from django.apps import AppConfig

class RecommenderConfig(AppConfig):
    name = "recommender"
    verbose_name = "PRLSS Recommender"

    def ready(self):
        try:
            from .ml_engine import load_model
            load_model()
        except Exception:
            pass
