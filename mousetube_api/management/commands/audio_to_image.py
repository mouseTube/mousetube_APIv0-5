import os
import time
import requests
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from mousetube_api.models import File
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

AUDIO_DIR = os.path.join(settings.BASE_DIR, "downloaded_audio")
IMG_DIR = os.path.join(settings.BASE_DIR, "audio_images")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

class Command(BaseCommand):
    help = "Download audio and generate spectrogram images (log scale)"

    def handle(self, *args, **options):
        logger.info("Starting audio spectrogram generation...")

        files = File.objects.exclude(link__isnull=True).exclude(link="")

        for file in files:
            url = file.link
            parsed = urlparse(url)

            if not url.startswith(("http://", "https://")):
                logger.warning(f"Invalid URL format: {url}")
                continue

            if parsed.hostname in ["localhost", "127.0.0.1"]:
                logger.info(f"Skipping local link: {url}")
                continue

            try:
                time.sleep(1)
                response = requests.head(url, allow_redirects=True, timeout=5)
                if response.status_code >= 400:
                    logger.warning(f"Unreachable URL: {url}")
                    continue
            except Exception as e:
                logger.warning(f"Error checking URL {url}: {e}")
                continue

            filename = os.path.basename(parsed.path)
            local_audio_path = os.path.join(AUDIO_DIR, filename)

            try:
                r = requests.get(url, stream=True, timeout=10)
                with open(local_audio_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"Downloaded {filename}")
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")
                continue

            try:
                y, sr = librosa.load(local_audio_path, sr=None)
                S = np.abs(librosa.stft(y))
                S_dB = librosa.amplitude_to_db(S, ref=np.max)

                plt.figure(figsize=(10, 4))
                librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='log')
                plt.colorbar(format="%+2.0f dB")
                plt.title(f"Spectrogram (log scale) - {filename}")
                plt.tight_layout()

                image_name = os.path.splitext(filename)[0] + ".png"
                image_path = os.path.join(IMG_DIR, image_name)
                plt.savefig(image_path)
                plt.close()
                logger.info(f"Saved spectrogram: {image_path}")

            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")