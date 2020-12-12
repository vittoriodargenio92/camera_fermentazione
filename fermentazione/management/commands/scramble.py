import random
from datetime import datetime, timedelta
from random import randrange

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from fermentazione.models import Sensor, Fermentation, Register


class Command(BaseCommand):
    help = 'Date Test'

    def handle(self, *args, **options):
        print('* Creo superuser...')
        User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
        print('* OK ')

        print('* Creo sensori...')
        interno = Sensor.objects.create(
            name="Interno",
            description="Sensore conntrollo temperatura interna",
            port="/dev/ttyUSB0",
            activation=True
        )

        esterno = Sensor.objects.create(
            name="Esterno",
            description="Sensore controllo temperatura esterna",
            port="/dev/ttyUSB1",
            activation=False
        )

        print('* OK ')

        start = datetime.now()
        finish = start + timedelta(days=10)

        print('* Creo fermentazione...')
        fermentazione = Fermentation.objects.create(
            name="Fermentazione Test",
            description="fermentazione test",
            start=start,
            finish=finish
        )

        fermentazione.sensors.add(interno)
        fermentazione.sensors.add(esterno)
        print('* OK ')

        print('* Creo registrazioni...')
        # Numero di registrazioni per 10 gg min * ore-giornaliere * giorni
        for hour in range(0, 24 * 10):
            Register.objects.create(
                time=start + timedelta(hours=hour),
                sensor=interno,
                temp_register=random.uniform(fermentazione.min_temp - 5, fermentazione.max_temp + 5)
            )

            Register.objects.create(
                time=start + timedelta(hours=hour),
                sensor=esterno,
                temp_register=random.uniform(fermentazione.min_temp - 5, fermentazione.max_temp + 5)
            )
            print("* registrazione {}".format(hour + 1))
        print('* OK ')


