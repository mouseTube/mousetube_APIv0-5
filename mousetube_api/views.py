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
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from .models import User, Strain, Subject, Protocol, Experiment, File
from django.db.models import Q


class FilePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
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
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '')
        filter_query = request.GET.get('filter', '')
        files = File.objects.all()
        if search_query:
            file_fields = [
                'file_number', 'link_file', 'notes_file', 'doi_file'
            ]

            # Fields for Experiment model
            experiment_fields = [
                'name_experiment', 'laboratory', 'group_subject', 'temperature',
                'light_cycle', 'microphone', 'acquisition_hardware', 'acquisition_software',
                'sampling_rate', 'bit_depth', 'date_experiment'
            ]

            # Fields for Subject model
            subject_fields = [
                'name_subject', 'origin_subject', 'sex_subject', 'group_subject',
                'genotype_subject', 'treatment'
            ]

            # Fields for User model (related to Subject)
            user_fields = [
                'name_user', 'first_name_user', 'email_user', 'unit_user',
                'institution_user', 'address_user', 'country_user'
            ]

            # Fields for Strain model (related to Subject)
            strain_fields = [
                'name_strain', 'background', 'biblio_strain'
            ]

            # Fields for Protocol model (related to Experiment)
            protocol_fields = [
                'name_protocol', 'number_files', 'protocol_description'
            ]

            # Build dynamic Q objects for File fields
            file_query = Q()
            for field in file_fields:
                file_query |= Q(**{f"{field}__icontains": search_query})

            # Build dynamic Q objects for Experiment fields
            experiment_query = Q()
            for field in experiment_fields:
                experiment_query |= Q(**{f"experiment__{field}__icontains": search_query})

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
                strain_query |= Q(**{f"subject__strain_subject__{field}__icontains": search_query})

            # Build dynamic Q objects for Protocol fields (via Experiment)
            protocol_query = Q()
            for field in protocol_fields:
                protocol_query |= Q(**{f"experiment__protocol__{field}__icontains": search_query})

            # Combine all queries
            files = files.filter(
                file_query | experiment_query | subject_query | user_query | strain_query | protocol_query
            )

        ALLOWED_FILTERS = ["is_valid_link"]

        # Apply filters
        if filter_query:
            for filter_name in filter_query.split(','):
                if filter_name not in ALLOWED_FILTERS:
                    continue  # Ignore invalid filters

                if filter_name == "is_valid_link":                    
                    files = files.filter(is_valid_link=True)
        
        # Add explicit ordering to avoid UnorderedObjectListWarning
        files = files.order_by('link_file')
        paginator = FilePagination()
        paginated_files = paginator.paginate_queryset(files, request)
        serializer = FileSerializer(paginated_files, many=True)
        return paginator.get_paginated_response(serializer.data)

