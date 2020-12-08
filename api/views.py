
from rest_framework import serializers

from rest_framework import viewsets
from rest_framework.response import Response

from fermentazione.models import Register


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Register
        fields = ['time', 'temp_register', ]


class RegisterViewSet(viewsets.ViewSet):
    serializer_class = RegisterSerializer
    queryset = Register.objects.all()

    def list(self, request):
        serializer = self.serializer_class(self.queryset.filter(sensor__activation=True), many=True)
        return Response(serializer.data)
