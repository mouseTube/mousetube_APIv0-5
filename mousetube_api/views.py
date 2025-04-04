'''
Created by Nicolas Torquet at 10/01/2025
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *


class UserAPIView(APIView):
    def get(self, *arg, **kwargs):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


class StrainAPIView(APIView):
    def get(self, *arg, **kwargs):
        strain = Strain.objects.all()
        serializers = StrainSerializer(strain, many=True)
        return Response(serializers.data)


class SubjectAPIView(APIView):
    def get(self, *arg, **kwargs):
        subject = Subject.objects.all()
        serializers = SubjectSerializer(subject, many=True)
        return Response(serializers.data)


class ProtocolAPIView(APIView):
    def get(self, *arg, **kwargs):
        protocol = Protocol.objects.all()
        serializers = ProtocolSerializer(protocol, many=True)
        return Response(serializers.data)


class ExperimentAPIView(APIView):
    def get(self, *arg, **kwargs):
        experiment = Experiment.objects.all()
        serializers = ExperimentSerializer(experiment, many=True)
        return Response(serializers.data)


class FileAPIView(APIView):
    def get(self, *arg, **kwargs):
        file = File.objects.all()
        serializers = FileSerializer(file, many=True)
        return Response(serializers.data)

