from __future__ import absolute_import
import os
from datetime import datetime
import time

import serial
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

import django

from camera_fermentazione.settings import MAX_DELAY_TEMP

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


def actions(is_active=None):
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(settings.RELAY_CHANNEL_HOT, GPIO.OUT)
        GPIO.setup(settings.RELAY_CHANNEL_COLD, GPIO.OUT)

        if is_active is None:
            GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.LOW)
            GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.LOW)
        elif is_active:
            GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.HIGH)
            GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.LOW)
        elif not is_active:
            GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.LOW)
            GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.HIGH)

    except ImportError:
        pass


@app.task(name="get_temp")
def get_temp():

    now = datetime.now()
    for fermentation in Fermentation.objects.filter(start__lte=now, finish__gte=now):
        for sensor in fermentation.sensors.all():
            ser = serial.Serial(sensor.port, 9600, timeout=1)
            ser.flush()
            while True:
                line = ser.readline().decode('utf-8').rstrip()
                if line:
                    temp = float(line)
                    register = Register.objects.create(
                        time=now,
                        sensor=sensor,
                        temp_register=temp
                    )
                    if register.sensor.activation:
                        if fermentation.is_correct(temp):
                            actions()
                        elif fermentation.is_height(temp): # Temperatura alta
                            actions(is_active=False)
                        elif fermentation.is_low(temp): # Temperatura bassa
                            actions(is_active=True)
                        register.save()
                    break
                time.sleep(1)




