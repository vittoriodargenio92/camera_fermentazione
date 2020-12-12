
from rest_framework import serializers, status

from rest_framework import viewsets
from rest_framework.response import Response

from fermentazione.models import Register


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Register
        fields = ['time', 'temp_register', ]


class RegisterRequestSerilizer(serializers.Serializer):
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=False)
    fermentation_id = serializers.IntegerField(required=True)


class RegisterChartResponseSerilizer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    internal = serializers.ListField(child=serializers.CharField())
    external = serializers.ListField(child=serializers.CharField())


class RegisterChartViewSet(viewsets.ViewSet):
    serializer_class = RegisterChartResponseSerilizer
    queryset = Register.objects.all()

    def create(self, request):
        request_serializer = RegisterRequestSerilizer(data=request.data)
        if request_serializer.is_valid():
            query_args = {
                "sensor__fermentation__id": request_serializer.data['fermentation_id'],
                "time__gte": request_serializer.data['start'],
            }

            if 'end' in request_serializer.data:
                query_args['time__lte'] = request_serializer.data['end']

            data = {
                "labels": [],
                "internal": [],
                "external": []
            }
            for register in self.queryset.filter(**query_args):
                if register.time not in data['labels']:
                    data['labels'].append(register.time)
                if register.sensor.activation:
                    data['internal'].append(int(register.temp_register))
                if not register.sensor.activation:
                    data['external'].append(int(register.temp_register))

            serilizer = RegisterChartResponseSerilizer(data=data)
            serilizer.is_valid()
            return Response(serilizer.data)
        else:
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
