from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User, Group

from fermentazione.models import Fermentation, Sensor, Register


class FermentationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_finish', 'start', 'finish', 'max_temp', 'min_temp']

    def is_finish(self, obj):
        return obj.finish < datetime.now()

    is_finish.boolean = True


class SensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'port', 'active', ]


class RegisterAdmin(admin.ModelAdmin):
    list_display = ['time', 'temp_register', 'get_sensor', 'get_fermentation']

    def get_sensor(self, obj):
        return obj.sensor.name

    def get_fermentation(self, obj):
        return obj.fermentation.name

    get_sensor.short_description = 'Sensor'
    get_fermentation.short_description = 'Fermentation'


admin.site.register(Fermentation, FermentationAdmin)
admin.site.register(Sensor, SensorAdmin)
admin.site.register(Register, RegisterAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)
