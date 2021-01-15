from django.db import models


class Sensor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    port = models.CharField(max_length=50)
    activation = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Fermentation(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    start = models.DateTimeField()
    finish = models.DateTimeField()
    temp = models.FloatField(default=22.00)
    delta = models.FloatField(default=0.50)
    sensors = models.ManyToManyField(Sensor, blank=True)

    def __str__(self):
        return self.name

    def is_height(self, t):
        return self.temp + self.delta > t

    def is_low(self, t):
        return self.temp - self.delta < t

    def is_correct(self, t):
        return self.temp - self.delta < t < self.temp + self.delta


class Register(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.DateTimeField()
    temp_register = models.FloatField(null=True, blank=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

