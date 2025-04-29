# Created by Nicolas Torquet at 10/01/2025
# torquetn@igbmc.fr
# Modified by Laurent Bouri 04/2025
# bouril@igbmc.fr
# Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
# CNRS - Mouse Clinical Institute
# PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
# Code under GPL v3.0 licence

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    UserSerializer,
    StrainSerializer,
    SubjectSerializer,
    ProtocolSerializer,
    ExperimentSerializer,
    FileSerializer,
    PageViewSerializer,
    TrackPageSerializer,
    SoftwareSerializer,
)
from .models import User, Strain, Subject, Protocol, Experiment, File, PageView, Software
from django.db.models import Q
from rest_framework import status
from django.utils.timezone import now
from django.db.models import F
from django.core.cache import cache
from django.core.management import call_command
from drf_spectacular.utils import extend_schema
from django.shortcuts import render
from django.conf import settings
import os


class FilePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class UserAPIView(APIView):
    serializer_class = UserSerializer

    def get(self, *arg, **kwargs):
        user = User.objects.all()
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data)


class StrainAPIView(APIView):
    serializer_class = StrainSerializer

    def get(self, *arg, **kwargs):
        strain = Strain.objects.all()
        serializers = self.serializer_class(strain, many=True)
        return Response(serializers.data)


class SubjectAPIView(APIView):
    serializer_class = SubjectSerializer

    def get(self, *arg, **kwargs):
        subject = Subject.objects.all()
        serializers = self.serializer_class(subject, many=True)
        return Response(serializers.data)


class ProtocolAPIView(APIView):
    serializer_class = ProtocolSerializer

    def get(self, *arg, **kwargs):
        protocol = Protocol.objects.all()
        serializers = self.serializer_class(protocol, many=True)
        return Response(serializers.data)


class ExperimentAPIView(APIView):
    serializer_class = ExperimentSerializer

    def get(self, *arg, **kwargs):
        experiment = Experiment.objects.all()
        serializers = self.serializer_class(experiment, many=True)
        return Response(serializers.data)


class FileAPIView(APIView):
    serializer_class = FileSerializer

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get("search", "")
        filter_query = request.GET.get("filter", "")
        files = File.objects.all()
        if search_query:
            file_fields = ["number", "link", "notes", "doi"]

            # Fields for Experiment model
            experiment_fields = [
                "name",
                "laboratory",
                "group_subject",
                "temperature",
                "light_cycle",
                "microphone",
                "acquisition_hardware",
                "acquisition_software",
                "sampling_rate",
                "bit_depth",
                "date",
            ]

            # Fields for Subject model
            subject_fields = [
                "name",
                "origin",
                "sex",
                "group",
                "genotype",
                "treatment",
            ]

            # Fields for User model (related to Subject)
            user_fields = [
                "name_user",
                "first_name_user",
                "email_user",
                "unit_user",
                "institution_user",
                "address_user",
                "country_user",
            ]

            # Fields for Strain model (related to Subject)
            strain_fields = ["name", "background", "bibliography"]

            # Fields for Protocol model (related to Experiment)
            protocol_fields = ["name", "number_files", "description"]

            # Build dynamic Q objects for File fields
            file_query = Q()
            for field in file_fields:
                file_query |= Q(**{f"{field}__icontains": search_query})

            # Build dynamic Q objects for Experiment fields
            experiment_query = Q()
            for field in experiment_fields:
                experiment_query |= Q(
                    **{f"experiment__{field}__icontains": search_query}
                )

            # Build dynamic Q objects for Subject fields
            subject_query = Q()
            for field in subject_fields:
                subject_query |= Q(**{f"subject__{field}__icontains": search_query})

            # Build dynamic Q objects for User fields (via Subject)
            user_query = Q()
            for field in user_fields:
                user_query |= Q(**{f"subject__user__{field}__icontains": search_query})

            # Build dynamic Q objects for Strain fields (via Subject)
            strain_query = Q()
            for field in strain_fields:
                strain_query |= Q(
                    **{f"subject__strain__{field}__icontains": search_query}
                )

            # Build dynamic Q objects for Protocol fields (via Experiment)
            protocol_query = Q()
            for field in protocol_fields:
                protocol_query |= Q(
                    **{f"experiment__protocol__{field}__icontains": search_query}
                )

            # Combine all queries
            files = files.filter(
                file_query
                | experiment_query
                | subject_query
                | user_query
                | strain_query
                | protocol_query
            )

        ALLOWED_FILTERS = ["is_valid_link"]

        # Apply filters
        if filter_query:
            for filter_name in filter_query.split(","):
                if filter_name not in ALLOWED_FILTERS:
                    continue  # Ignore invalid filters

                if filter_name == "is_valid_link":
                    files = files.filter(is_valid_link=True)

        # Add explicit ordering to avoid UnorderedObjectListWarning
        files = files.order_by("link")
        paginator = FilePagination()
        paginated_files = paginator.paginate_queryset(files, request)
        serializer = self.serializer_class(paginated_files, many=True)
        return paginator.get_paginated_response(serializer.data)


class SoftwareAPIView(APIView):
    serializer_class = SoftwareSerializer

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get("search", "")
        filter_query = request.GET.get("filter", "")
        softwares = Software.objects.all()

        if search_query:
            software_fields = [
                "software_name",
                "software_type",
                "made_by",
                "description",
                "technical_requirements",
            ]

            reference_fields = [
                "name_reference",
                "description",
                "url",
                "doi",
            ]

            user_fields = [
                "name_user",
                "first_name_user",
                "email_user",
                "unit_user",
                "institution_user",
                "address_user",
                "country_user",
            ]

            # Build Q objects
            software_query = Q()
            for field in software_fields:
                software_query |= Q(**{f"{field}__icontains": search_query})

            reference_query = Q()
            for field in reference_fields:
                reference_query |= Q(
                    **{f"references_and_tutorials__{field}__icontains": search_query}
                )

            user_query = Q()
            for field in user_fields:
                user_query |= Q(**{f"users__{field}__icontains": search_query})

            # Combine all
            softwares = softwares.filter(software_query | reference_query | user_query).distinct()

        ALLOWED_FILTERS = ["software_type"]

        if filter_query:
            for filter_name in filter_query.split(","):
                if filter_name not in ALLOWED_FILTERS:
                    continue

                if filter_name == "software_type":
                    value = request.GET.get("software_type")
                    if value:
                        softwares = softwares.filter(software_type=value)

        softwares = softwares.order_by("software_name")
        paginator = FilePagination()
        paginated_softwares = paginator.paginate_queryset(softwares, request)
        serializer = self.serializer_class(paginated_softwares, many=True)
        return paginator.get_paginated_response(serializer.data)


class TrackPageView(APIView):
    serializer_class = TrackPageSerializer

    @extend_schema(exclude=True)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        path = serializer.validated_data["path"]

        today = now().date()

        obj, created = PageView.objects.get_or_create(
            path=path, date=today, defaults={"count": 1}
        )

        if not created:
            PageView.objects.filter(pk=obj.pk).update(count=F("count") + 1)

        cache_key = f"pageview-log-generated-{today}"

        if not cache.get(cache_key):
            call_command("export_page_view", verbosity=0)
            cache.set(cache_key, True, 60 * 60 * 24)

        return Response(PageViewSerializer(obj).data, status=status.HTTP_200_OK)


def stats_view(request):
    year = now().year
    filename = f"stats_{year}.html"
    output_path = os.path.join(settings.LOGS_DIR, filename)

    if not os.path.exists(output_path):
        return render(request, "error.html", {"message": "Stat file not found!"})

    with open(output_path, "r") as f:
        content = f.read()

    return render(request, "stats_view.html", {"content": content})
