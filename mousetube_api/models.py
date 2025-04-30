# Created by Nicolas Torquet at 09/01/2025
# torquetn@igbmc.fr
# Modified by Laurent Bouri 04/2025
# bouril@igbmc.fr
# Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
# CNRS - Mouse Clinical Institute
# PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
# Code under GPL v3.0 licence

from django.db import models


class User(models.Model):
    """
    Represents a user of the system.

    Attributes:
        name_user (str): The last name of the user.
        first_name_user (str): The first name of the user.
        email_user (str): The email address of the user.
        unit_user (str, optional): The unit the user belongs to.
        institution_user (str, optional): The institution the user belongs to.
        address_user (str, optional): The address of the user.
        country_user (str, optional): The country of the user.
    """

    name_user = models.CharField(max_length=255, null=True)
    first_name_user = models.CharField(max_length=255, null=True)
    email_user = models.CharField(max_length=255)
    unit_user = models.CharField(max_length=255, blank=True, null=True)
    institution_user = models.CharField(max_length=255, blank=True, null=True)
    address_user = models.CharField(max_length=255, blank=True, null=True)
    country_user = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """
        Returns the full name of the user.

        Returns:
            str: The full name of the user.
        """
        return f"{self.first_name_user} {self.name_user}"


class Strain(models.Model):
    """
    Represents a strain of a mouse.

    Attributes:
        name (str): The name of the strain.
        background (str): The genetic background of the strain.
        bibliography (str, optional): Bibliographical references related to the strain.
    """

    name = models.CharField(max_length=255, unique=True)
    background = models.CharField(max_length=255)
    bibliography = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Returns the name of the strain as a string.

        Returns:
            str: The name of the strain.
        """
        return self.name

    class Meta:
        verbose_name = "Strain"
        verbose_name_plural = "Strains"


class Subject(models.Model):
    """
    Represents a subject (mouse) in the system.

    Attributes:
        name (str): The name of the subject.
        strain (Strain): The strain associated with the subject.
        origin (str, optional): The origin of the subject.
        sex (str, optional): The sex of the subject.
        group (str, optional): The group the subject belongs to.
        genotype (str, optional): The genotype of the subject.
        treatment (str, optional): The treatment applied to the subject.
        user (User): The user associated with the subject.
    """

    SEX_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    name = models.CharField(max_length=255, unique=True)
    strain = models.ForeignKey(Strain, on_delete=models.CASCADE)
    origin = models.CharField(max_length=255, blank=True, null=True)
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, blank=True, null=True)
    group = models.CharField(max_length=255, blank=True, null=True)
    genotype = models.CharField(max_length=255, blank=True, null=True)
    treatment = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns the name of the subject.

        Returns:
            str: The name of the subject.
        """
        return self.name

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


class Protocol(models.Model):
    """
    Represents an experimental protocol.

    Attributes:
        name (str): The name of the protocol.
        number_files (int, optional): The number of files associated with the protocol.
        description (str): A description of the protocol.
        user (User): The user associated with the protocol.
    """

    name = models.CharField(max_length=255)
    number_files = models.IntegerField(blank=True, null=True)
    description = models.TextField(default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns the name of the protocol.

        Returns:
            str: The name of the protocol.
        """
        return self.name

    class Meta:
        verbose_name = "Protocol"
        verbose_name_plural = "Protocols"


class Experiment(models.Model):
    """
    Represents an experiment.

    Attributes:
        name (str): The name of the experiment.
        protocol (Protocol): The protocol associated with the experiment.
        group_subject (str, optional): The group of subjects involved in the experiment.
        date (date, optional): The date of the experiment.
        temperature (str, optional): The temperature during the experiment.
        light_cycle (str, optional): The light cycle during the experiment.
        microphone (str, optional): The microphone used in the experiment.
        acquisition_hardware (str, optional): The hardware used for acquisition.
        acquisition_software (str, optional): The software used for acquisition.
        sampling_rate (float, optional): The sampling rate of the data.
        bit_depth (float, optional): The bit depth of the data.
        laboratory (str, optional): The laboratory where the experiment was conducted.
    """

    name = models.CharField(max_length=255, unique=True)
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    group_subject = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    temperature = models.CharField(max_length=255, blank=True, null=True)
    light_cycle = models.CharField(max_length=255, blank=True, null=True)
    microphone = models.CharField(max_length=255, blank=True, null=True)
    acquisition_hardware = models.CharField(max_length=255, blank=True, null=True)
    acquisition_software = models.CharField(max_length=255, blank=True, null=True)
    sampling_rate = models.FloatField(blank=True, null=True)
    bit_depth = models.FloatField(blank=True, null=True)
    laboratory = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """
        Returns the name of the experiment.

        Returns:
            str: The name of the experiment.
        """
        return self.name

    class Meta:
        verbose_name = "Experiment"
        verbose_name_plural = "Experiments"


class File(models.Model):
    """
    Represents a file associated with an experiment or subject.

    Attributes:
        experiment (Experiment, optional): The experiment associated with the file.
        subject (Subject, optional): The subject associated with the file.
        number (int, optional): The number of the file.
        link (str, optional): The URL link to the file.
        notes (str, optional): Notes about the file.
        doi (str, optional): The DOI of the file.
        is_valid_link (bool): Whether the link is valid.
        donwloads (int): The number of downloads for the file.
    """

    experiment = models.ForeignKey(
        Experiment, on_delete=models.CASCADE, blank=True, null=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, blank=True, null=True
    )
    number = models.IntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    doi = models.CharField(max_length=255, blank=True, null=True)
    is_valid_link = models.BooleanField(default=False)
    downloads = models.IntegerField(default=0)

    def __str__(self):
        """
        Returns the link to the file.

        Returns:
            str: The URL link to the file.
        """
        return self.link

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"


class PageView(models.Model):
    """
    Represents a page view for tracking purposes.

    Attributes:
        path (str): The path of the page.
        date (date): The date of the page view.
        count (int): The number of views for the page on the given date.
    """

    path = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("path", "date")

    def __str__(self):
        """
        Returns a string representation of the page view.

        Returns:
            str: The path, date, and count of the page view.
        """
        return f"{self.path} - {self.date} ({self.count})"


class Reference(models.Model):
    name_reference = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    doi = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name_reference

    class Meta:
        verbose_name = 'Reference'
        verbose_name_plural = 'References'


class Software(models.Model):
    CHOICES_SOFTWARE = (
        ("acquisition", "acquisition"),
        ("analysis", "analysis"),
        ("acquisition and analysis", "acquisition and analysis")
    )

    software_name = models.CharField(max_length=255)
    software_type = models.CharField(max_length=255, null=True, default="acquisition", choices=CHOICES_SOFTWARE)
    made_by = models.TextField(default='', blank=True)
    description = models.TextField(default='', blank=True)
    technical_requirements = models.TextField(default='', blank=True)
    references_and_tutorials = models.ManyToManyField(Reference, related_name='software', blank=True)
    users = models.ManyToManyField(User, related_name='software_to_user', blank=True)

    def __str__(self):
        return self.software_name

    class Meta:
        verbose_name = 'Software'
        verbose_name_plural = 'Software'
