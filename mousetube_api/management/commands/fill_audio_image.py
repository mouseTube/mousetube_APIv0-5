import os
from django.core.management.base import BaseCommand
from django.conf import settings
from mousetube_api.models import File


class Command(BaseCommand):
    help = "Fill the spectrogram_image field for audio files with the corresponding image file."

    def handle(self, *args, **options):
        image_dir = os.path.join(settings.MEDIA_ROOT, "audio_images")
        if not os.path.isdir(image_dir):
            self.stderr.write(self.style.ERROR(f"Folder not found : {image_dir}"))
            return

        image_files = {f for f in os.listdir(image_dir) if f.endswith(".png")}
        updated = 0

        for file in File.objects.exclude(link__isnull=True).exclude(link=""):
            base_name = os.path.basename(file.link)
            print(f"Base name: {base_name}")
            base_name = os.path.splitext(base_name)[0]
            image_name = f"{base_name}.png"
            if image_name in image_files:
                if not file.spectrogram_image:
                    file.spectrogram_image = os.path.join("audio_images", image_name)
                    file.save()
                    updated += 1
                    self.stdout.write(f"✔ File updated : {base_name}")
                else:
                    self.stdout.write(f"… Field already filled : {base_name}")

        self.stdout.write(self.style.SUCCESS(f"{updated} file updated."))
