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

    def add_arguments(self, parser):
        parser.add_argument(
            '--quality',
            type=str,
            choices=['low', 'medium', 'high'],
            default='medium',
            help='Spectrogram quality: low (faster), medium (default), high (slower but detailed)'
        )
        parser.add_argument(
            '--local',
            action='store_true',
            help='Process only local audio files already in the downloaded_audio directory'
        )

    def handle(self, *args, **options):
        logger.info("Starting audio spectrogram generation...")

        quality = options['quality']
        local_mode = options['local']

        if quality == 'low':
            n_fft = 512
            hop_length = 256
        elif quality == 'high':
            n_fft = 2048
            hop_length = 512
        else:  # medium
            n_fft = 1024
            hop_length = 256

        logger.info(f"Using quality '{quality}': n_fft={n_fft}, hop_length={hop_length}")

        if local_mode:
            files = [f for f in os.listdir(AUDIO_DIR) if os.path.isfile(os.path.join(AUDIO_DIR, f))]
            for filename in files:
                self.generate_spectrogram(filename, os.path.join(AUDIO_DIR, filename), sr=300000, n_fft=n_fft, hop_length=hop_length)
        else:
            for file in File.objects.exclude(link__isnull=True).exclude(link=""):
                url = file.link
                parsed = urlparse(url)

                if not url.startswith(("http://", "https://")):
                    logger.warning(f"Invalid URL format: {url}")
                    continue

                if parsed.hostname in ["localhost", "127.0.0.1"]:
                    logger.info(f"Skipping local link: {url}")
                    continue

                try:
                    time.sleep(1)  # Be gentle with the server
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

                    self.generate_spectrogram(filename, local_audio_path, sr=300000, n_fft=n_fft, hop_length=hop_length)

                    os.remove(local_audio_path)
                    logger.info(f"Deleted audio file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to download or process {url}: {e}")
                    continue

    def generate_spectrogram(self, filename, local_audio_path, sr, n_fft, hop_length):
        try:
            audio_length = librosa.get_duration(path=local_audio_path)
            logger.info(f"Audio length for {filename}: {audio_length} seconds")
            logger.info(f"Generating spectrogram for {filename}...")
            y, sr = librosa.load(local_audio_path, sr=sr, mono=True, duration=10)
            logger.info(f"Loaded {filename} with sample rate {sr}")
            S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
            logger.info(f"Computed STFT for {filename}")
            S_dB = librosa.amplitude_to_db(S, ref=np.max)

            plt.figure(figsize=(10, 4))
            logger.info(f"Plotting spectrogram for {filename}...")
            librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='linear')
            logger.info(f"Displayed spectrogram for {filename}...")
            plt.ylim(20000, 150000)
            plt.colorbar(format="%+2.0f dB")
            plt.title(f"Spectrogram - {filename}")
            plt.tight_layout()

            image_name = os.path.splitext(filename)[0] + ".png"
            image_path = os.path.join(IMG_DIR, image_name)
            logger.info(f"Saving spectrogram to {image_path}...")
            plt.savefig(image_path)
            plt.close()
            logger.info(f"Saved spectrogram: {image_path}")
        except Exception as e:
            logger.error(f"Error generating spectrogram for {filename}: {e}")