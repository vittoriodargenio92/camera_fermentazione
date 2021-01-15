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
import RPi.GPIO as GPIO

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


def off_all():
    GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.HIGH)
    GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.HIGH)


def off_hot():
    GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.HIGH)


def off_cold():
    GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.HIGH)


def on_all():
    GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.LOW)
    GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.LOW)


def on_hot():
    GPIO.output(settings.RELAY_CHANNEL_HOT, GPIO.LOW)


def on_cold():
    GPIO.output(settings.RELAY_CHANNEL_COLD, GPIO.LOW)


def actions(is_active=None):
    try:

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(settings.RELAY_CHANNEL_HOT, GPIO.OUT)
        GPIO.setup(settings.RELAY_CHANNEL_COLD, GPIO.OUT)

        if is_active is None:
            off_all()
        elif is_active:
            off_cold()
            on_hot()
        elif not is_active:
            off_cold()
            on_cold()

    except ImportError:
        pass


@app.task(name="reset_all")
def commad_relay(command=None, slug=None):
    if command and slug:
        if command == 'OFF':
            if slug == 'ALL':
                actions()
            elif slug == 'HOT':
                actions(is_active=True)
            elif slug == 'COLD':
                actions(is_active=False)
        elif command == 'ON':
            if slug == 'ALL':
                actions()
            elif slug == 'HOT':
                actions(is_active=True)
            elif slug == 'COLD':
                actions(is_active=False)


@app.task(name="get_temp")
def get_temp():
    now = datetime.now()
    fermentations = Fermentation.objects.filter(start__lte=now, finish__gte=now)
    if not fermentations:
        actions()

    for fermentation in fermentations:
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
                        if fermentation.is_correct(temp):  # Temperatura giusta
                            actions()
                        elif fermentation.is_height(temp):  # Temperatura alta
                            actions(is_active=True)
                        elif fermentation.is_low(temp):  # Temperatura bassa
                            actions(is_active=False)
                        register.save()
                    break
                time.sleep(1)
