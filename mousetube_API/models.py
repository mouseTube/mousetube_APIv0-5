'''
Created by Nicolas Torquet at 09/01/2025
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class User(models.Model):
    name_user = models.CharField(max_length=255)
    first_name_user = models.CharField(max_length=255)
    email_user = models.CharField(max_length=255)
    unit_user = models.CharField(max_length=255, blank=True, null=True)
    institution_user = models.CharField(max_length=255, blank=True, null=True)
    address_user = models.CharField(max_length=255, blank=True, null=True)
    country_user = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name_user} {self.name_user}"

class Strain(models.Model):
    name_strain = models.CharField(max_length=255, unique=True)
    background = models.CharField(max_length=255)
    biblio_strain = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name_strain

    class Meta:
        verbose_name = 'Strain'
        verbose_name_plural = 'Strains'


class Subject(models.Model):
    name_subject = models.CharField(max_length=255, unique=True)
    strain_subject = models.ForeignKey(Strain, on_delete=models.CASCADE)
    origin_subject = models.CharField(max_length=255, blank=True, null=True)
    sex_subject = models.CharField(max_length=255, blank=True, null=True)
    group_subject = models.CharField(max_length=255, blank=True, null=True)
    genotype_subject = models.CharField(max_length=255, blank=True, null=True)
    treatment = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_subject

    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'


class Protocol(models.Model):
    name_protocol = models.CharField(max_length=255)
    number_files = models.IntegerField(blank=True, null=True)
    protocol_description = models.TextField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_protocol

    class Meta:
        verbose_name = 'Protocol'
        verbose_name_plural = 'Protocols'


class Experiment(models.Model):
    name_experiment = models.CharField(max_length=255, unique=True)
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    group_subject = models.CharField(max_length=255, blank=True, null=True)
    date_experiment = models.DateField(blank=True, null=True)
    temperature = models.CharField(max_length=255, blank=True, null=True)
    light_cycle = models.CharField(max_length=255, blank=True, null=True)
    microphone = models.CharField(max_length=255, blank=True, null=True)
    acquisition_hardware = models.CharField(max_length=255, blank=True, null=True)
    acquisition_software = models.CharField(max_length=255, blank=True, null=True)
    sampling_rate = models.FloatField(blank=True, null=True)
    bit_depth = models.FloatField(blank=True, null=True)
    laboratory = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name_experiment

    class Meta:
        verbose_name = 'Experiment'
        verbose_name_plural = 'Experiments'


class File(models.Model):
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_number = models.IntegerField(blank=True, null=True)
    link_file = models.URLField(blank=True, null=True)
    doi_file = models.CharField(max_length=255, blank=True, null=True)
    note_file = models.TextField(blank=True, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return self.link_file

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'