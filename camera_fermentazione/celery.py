from __future__ import absolute_import
import os
from datetime import datetime
import time

import serial
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

import django
from django.utils import timezone

django.setup()

# set the default Django settings module for the 'celery' program.
from fermentazione.models import Fermentation, Sensor, Register

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'camera_fermentazione.settings')
app = Celery('camera_fermentazione')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/1'),
        get_temp.s(),
    )


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(name="get_temp")
def get_temp():
    fermentation = Fermentation.objects.filter(
        start__lte=timezone.now(),
        finish__gte=timezone.now()
    ).first()

    if fermentation:
        sensors = Sensor.objects.filter(active=True)

        for sensor in sensors:
            ser = serial.Serial(sensor.port, 9600, timeout=1)
            ser.flush()

            while True:
                line = ser.readline().decode('utf-8').rstrip()
                if line:
                    temp = float(line)
                    Register.objects.create(
                        time=timezone.now(),
                        sensor=sensor,
                        temp_register=temp,
                        fermentation=fermentation
                    )
                    break
                time.sleep(1)

