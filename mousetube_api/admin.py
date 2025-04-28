from django.contrib import admin
from .models import User, Strain, Subject, Protocol, Experiment, File


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name_user",
        "name_user",
        "email_user",
        "unit_user",
        "institution_user",
        "country_user",
    )
    search_fields = ("first_name_user", "name_user", "email_user")
    list_filter = ("country_user",)


class StrainAdmin(admin.ModelAdmin):
    list_display = ("name", "background")
    search_fields = ("name",)
    list_filter = ("background",)


class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "strain",
        "user",
        "sex",
        "genotype",
    )
    search_fields = (
        "name",
        "strain__name",
        "user__first_name_user",
    )
    list_filter = ("strain", "sex", "user")


class ProtocolAdmin(admin.ModelAdmin):
    list_display = ("name", "number_files", "user")
    search_fields = ("name", "user__first_name_user")
    list_filter = ("user",)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "protocol",
        "date",
        "temperature",
        "light_cycle",
        "sampling_rate",
    )
    search_fields = ("name", "protocol__name")
    list_filter = ("protocol", "date")


class FileAdmin(admin.ModelAdmin):
    list_display = (
        "experiment",
        "subject",
        "number",
        "link",
        "doi",
        "is_valid_link",
    )
    search_fields = (
        "link",
        "doi",
        "experiment__name",
        "subject__name",
    )
    list_filter = ("is_valid_link", "experiment", "subject")


admin.site.register(User, UserAdmin)
admin.site.register(Strain, StrainAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(File, FileAdmin)
