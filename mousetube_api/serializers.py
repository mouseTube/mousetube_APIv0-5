'''
Created by Nicolas Torquet at 10/01/2025
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

from rest_framework import serializers
from mousetube_api.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MousetubeUser
        fields = '__all__'


class StrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    strain_subject = StrainSerializer(read_only=True)
    class Meta:
        model = Subject
        fields = '__all__'


class ProtocolSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Protocol
        fields = '__all__'

class ExperimentSerializer(serializers.ModelSerializer):
    protocol = ProtocolSerializer(read_only=True)
    class Meta:
        model = Experiment
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    experiment = ExperimentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class Meta:
        model = File
        fields = '__all__'

