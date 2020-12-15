from datetime import datetime, timedelta

from rest_framework import serializers, status

from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from fermentazione.models import Register, Fermentation
from django.db.models import Avg


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Register
        fields = ['time', 'temp_register', ]


class RegisterRequestserializer(serializers.Serializer):
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=True)
    fermentation_id = serializers.IntegerField(required=True)


class RegisterChartResponseserializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    internal = serializers.ListField(child=serializers.CharField())
    external = serializers.ListField(child=serializers.CharField())

class RegisterChartBarResponseserializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    avg = serializers.ListField(child=serializers.CharField())


class RegisterChartViewSet(viewsets.ViewSet):
    serializer_class = RegisterChartResponseserializer
    queryset = Register.objects.all()

    def create(self, request):
        request_serializer = RegisterRequestserializer(data=request.data)
        if request_serializer.is_valid():
            query_args = {
                "sensor__fermentation__id": request_serializer.data['fermentation_id'],
                "time__gte": request_serializer.data['start'],
                "time__lte": request_serializer.data['end'],
                "time__minute__in": [i for i in range(0, 60, 10)]
            }

            data = {
                "labels": [],
                "internal": [],
                # "external": []
            }
            for register in self.queryset.filter(**query_args):
                if register.time not in data['labels']:
                    data['labels'].append(register.time.strftime("%m/%d/%Y %H:%M"))
                if register.sensor.activation:
                    data['internal'].append(round(register.temp_register))
                # if not register.sensor.activation:
                #     data['external'].append(round(register.temp_register))

            serializer = RegisterChartResponseserializer(data=data)
            serializer.is_valid()
            return Response(serializer.data)
        else:
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterChartMegiaGiorniViewSet(viewsets.ViewSet):
    serializer_class = RegisterChartResponseserializer
    queryset = Register.objects.all()

    def create(self, request):
        request_serializer = RegisterRequestserializer(data=request.data)

        if request_serializer.is_valid():
            start = datetime.strptime(request_serializer.data['start'], '%Y-%m-%d')
            end = datetime.strptime(request_serializer.data['end'], '%Y-%m-%d')
            start = start.replace(hour=0, minute=0, second=0)
            end = end.replace(hour=23, minute=59, second=59)
            delta = end - start

            data = {
                "labels": [],
                "avg": []
            }

            for day in range(0, delta.days + 1):
                label = (start + timedelta(days=day))
                data['labels'].append(label.strftime("%m/%d/%Y"))

                start_q = start + timedelta(days=day)
                end_q = end.replace(day=start_q.day)

                query_args = {
                    "sensor__fermentation__id": request_serializer.data['fermentation_id'],
                    "time__gte": start_q,
                    "time__lte": end_q,
                }
                q = self.queryset.filter(**query_args).aggregate(Avg('temp_register'))
                if q['temp_register__avg']:
                    data["avg"].append(round(q['temp_register__avg']))
                else:
                    data["avg"].append(0)

            serializer = RegisterChartBarResponseserializer(data=data)
            serializer.is_valid()
            return Response(serializer.data)
        else:
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

## temperature totali (torta)


class FermentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fermentation
        fields = ['name', 'start', 'finish', ]


class FermentationViewSet(viewsets.ViewSet):
    serializer_class = FermentationSerializer
    queryset = Fermentation.objects.all()

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)
