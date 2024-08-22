from .models import Binnacle

def log_to_binnacle(action, details):
    Binnacle.objects.create(action=action, details=details)