from django.db import models


class Fermentation(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    start = models.DateTimeField()
    finish = models.DateTimeField()
    max_temp = models.FloatField(default=18.00)
    min_temp = models.FloatField(default=22.00)


class Sensor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    port = models.CharField(max_length=50)
    activation = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


class Register(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.DateTimeField()
    temp_register = models.FloatField(null=True, blank=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    fermentation = models.ForeignKey(Fermentation, on_delete=models.CASCADE)
