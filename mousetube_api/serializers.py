# Created by Nicolas Torquet at 10/01/2025
# torquetn@igbmc.fr
# Modified by Laurent Bouri 04/2025
# bouril@igbmc.fr
# Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
# CNRS - Mouse Clinical Institute
# PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
# Code under GPL v3.0 licence


from mousetube_api.models import (
    User,
    Strain,
    Subject,
    Protocol,
    Experiment,
    File,
    PageView,
    Software,
    Reference,
)
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class StrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    strain = StrainSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"


class ProtocolSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Protocol
        fields = "__all__"


class ExperimentSerializer(serializers.ModelSerializer):
    protocol = ProtocolSerializer(read_only=True)

    class Meta:
        model = Experiment
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    experiment = ExperimentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = File
        fields = "__all__"


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = "__all__"


class SoftwareSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = Software
        fields = "__all__"


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = "__all__"


class TrackPageSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=255)
