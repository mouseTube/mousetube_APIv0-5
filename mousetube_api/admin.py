from django.contrib import admin
from .models import User, Strain, Subject, Protocol, Experiment, File, PageView
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html



class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name_user', 'name_user', 'email_user', 'unit_user', 'institution_user', 'country_user')
    search_fields = ('first_name_user', 'name_user', 'email_user')
    list_filter = ('country_user',)


class StrainAdmin(admin.ModelAdmin):
    list_display = ('name_strain', 'background')
    search_fields = ('name_strain',)
    list_filter = ('background',)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name_subject', 'strain_subject', 'user', 'sex_subject', 'genotype_subject')
    search_fields = ('name_subject', 'strain_subject__name_strain', 'user__first_name_user')
    list_filter = ('strain_subject', 'sex_subject', 'user')


class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name_protocol', 'number_files', 'user')
    search_fields = ('name_protocol', 'user__first_name_user')
    list_filter = ('user',)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name_experiment', 'protocol', 'date_experiment', 'temperature', 'light_cycle', 'sampling_rate')
    search_fields = ('name_experiment', 'protocol__name_protocol')
    list_filter = ('protocol', 'date_experiment')


class FileAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'subject', 'file_number', 'link_file', 'doi_file', 'is_valid_link')
    search_fields = ('link_file', 'doi_file', 'experiment__name_experiment', 'subject__name_subject')
    list_filter = ('is_valid_link', 'experiment', 'subject')


admin.site.register(User, UserAdmin)
admin.site.register(Strain, StrainAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(File, FileAdmin)