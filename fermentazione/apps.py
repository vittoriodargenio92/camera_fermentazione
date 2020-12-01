from django.apps import AppConfig
from django.conf import settings


class FermentazioneConfig(AppConfig):
    name = 'fermentazione'

    def ready(self):
        try:
            import RPi.GPIO as GPIO

            # GPIO setup
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(settings.RELAY_CHANNEL, GPIO.OUT)
        except:
            print('Non è il raspberry')
