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
from scipy.ndimage import uniform_filter1d, maximum_filter1d
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)

# Directories for downloaded audio and spectrogram images
AUDIO_DIR = os.path.join(settings.BASE_DIR, "downloaded_audio")
IMG_DIR = settings.AUDIO_IMG_DIR
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)


class Command(BaseCommand):
    help = "Download audio and generate spectrogram images (log scale)"

    def add_arguments(self, parser):
        # Add command line arguments
        parser.add_argument(
            "--quality",
            type=str,
            choices=["low", "medium", "high"],
            default="medium",
            help="Spectrogram quality: low (faster), medium (default), high (slower but detailed)",
        )
        parser.add_argument(
            "--local",
            action="store_true",
            help="Process only local audio files already in the downloaded_audio directory",
        )
        parser.add_argument(
            "--filtered-only",
            action="store_true",
            help="Generate spectrogram image only if a signal is detected (10s after detection)",
        )

    @staticmethod
    def is_valid_audio_file(filename):
        VALID_EXTENSIONS = {
            ".wav",
            ".wave",
            ".flac",
            ".mp3",
            ".ogg",
            ".m4a",
            ".aiff",
            ".aif",
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext in VALID_EXTENSIONS

    def handle(self, *args, **options):
        logger.info("Starting audio spectrogram generation...")

        quality = options["quality"]
        local_mode = options["local"]
        filtered_only = options["filtered_only"]

        # Set FFT and hop length based on the quality parameter
        if quality == "low":
            n_fft = 512
            hop_length = 256
        elif quality == "high":
            n_fft = 2048
            hop_length = 512
        else:  # medium
            n_fft = 1024
            hop_length = 256

        logger.info(
            f"Using quality '{quality}': n_fft={n_fft}, hop_length={hop_length}"
        )

        if local_mode:
            # Process local audio files from the downloaded_audio directory
            files = [
                f
                for f in os.listdir(AUDIO_DIR)
                if os.path.isfile(os.path.join(AUDIO_DIR, f))
            ]
            for filename in files:
                if not self.is_valid_audio_file(filename):
                    logger.info(f"Skipping unsupported audio file format: {filename}")
                    continue
                self.generate_spectrogram(
                    filename,
                    os.path.join(AUDIO_DIR, filename),
                    sr=300000,
                    n_fft=n_fft,
                    hop_length=hop_length,
                    filtered_only=filtered_only,
                )
        else:
            # Process files from the database if the local option is not specified
            for file in File.objects.exclude(link__isnull=True).exclude(link=""):
                url = file.link
                parsed = urlparse(url)

                # Skip invalid or local URLs
                if not url.startswith(("http://", "https://")):
                    logger.warning(f"Invalid URL format: {url}")
                    continue

                if parsed.hostname in ["localhost", "127.0.0.1"]:
                    logger.info(f"Skipping local link: {url}")
                    continue

                try:
                    time.sleep(1)  # Sleep to prevent overloading the server
                    response = requests.head(url, allow_redirects=True, timeout=5)
                    if response.status_code >= 400:
                        logger.warning(f"Unreachable URL: {url}")
                        continue
                except Exception as e:
                    logger.warning(f"Error checking URL {url}: {e}")
                    continue

                filename = os.path.basename(parsed.path)
                local_audio_path = os.path.join(AUDIO_DIR, filename)

                if not self.is_valid_audio_file(filename):
                    logger.info(f"Skipping unsupported audio file format: {filename}")
                    continue

                try:
                    # Download the audio file
                    r = requests.get(url, stream=True, timeout=10)
                    with open(local_audio_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logger.info(f"Downloaded {filename}")

                    # Generate the spectrogram for the downloaded audio
                    self.generate_spectrogram(
                        filename,
                        local_audio_path,
                        sr=300000,
                        n_fft=n_fft,
                        hop_length=hop_length,
                        filtered_only=filtered_only,
                    )

                    os.remove(
                        local_audio_path
                    )  # Remove the local audio file after processing
                    logger.info(f"Deleted audio file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to download or process {url}: {e}")
                    continue

    def generate_spectrogram(
        self, filename, local_audio_path, sr, n_fft, hop_length, filtered_only
    ):
        """
        Generates a spectrogram image for a given audio file.

        This function detects whether the audio contains a relevant signal (e.g., ultrasonic vocalizations)
        and generates a spectrogram accordingly. If `filtered_only` is True, spectrograms are only
        generated when signal is detected above a computed threshold.

        Parameters:
        - filename (str): Name of the audio file (used for display and output file naming).
        - local_audio_path (str): Path to the audio file to load and analyze.
        - sr (int): Sampling rate used when loading the audio.
        - n_fft (int): FFT window size for computing the spectrogram; affects frequency resolution.
        - hop_length (int): Number of audio samples between STFT columns; affects time resolution.
        - filtered_only (bool): If True, spectrograms are only generated when a detectable signal is present.

        Signal Filtering Parameters:
        - `freq_min` / `freq_max` (20000–150000 Hz): Defines the frequency band to analyze; important for targeting ultrasonic ranges (e.g., mouse USVs).
        - `size=7`: The smoothing filter size applied to the frequency-band power curve; higher values smooth out noise more but can blur short signals.
        - `+3 dB`: A dynamic threshold is computed as the median power + 3 dB; this offset can be increased to make detection stricter.
        - `0.03 sec`: Minimum duration (in seconds) the signal must exceed the threshold to be considered valid (computed in frames via hop length).

        Returns:
        None. Saves the spectrogram as an image in IMG_DIR and updates the File instance with the path.
        """
        try:
            logger.info(f"Analyzing {filename}...")

            # Load the audio file
            y, sr = librosa.load(local_audio_path, sr=sr, mono=True)
            logger.info(f"Audio loaded: {filename} (duration: {len(y) / sr:.2f}s)")

            # Compute the short-time Fourier transform (STFT)
            S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
            S_dB = librosa.amplitude_to_db(S, ref=np.max)

            # Filter frequencies to focus on a specific range
            freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
            freq_min, freq_max = 20000, 150000
            freq_mask = (freqs >= freq_min) & (freqs <= freq_max)
            band_power = S_dB[freq_mask, :].mean(axis=0)

            # filter the power values
            max_filtered_power = maximum_filter1d(band_power, size=15)
            filtered_power = uniform_filter1d(max_filtered_power, size=5)

            # Use mean and std for thresholding
            threshold_db = np.mean(filtered_power) + 2 * np.std(filtered_power)

            # Alternative thresholding method
            # Compute median and IQR
            # median_power = np.median(filtered_power)
            # q75, q25 = np.percentile(filtered_power, [75, 25])
            # iqr = q75 - q25

            # Threshold using median and IQR
            # threshold_db = median_power + 1.5 * iqr

            logger.info(
                f"Mean power: {np.mean(filtered_power):.2f} dB, Threshold: {threshold_db:.2f} dB"
            )
            logger.info(f"Max power: {np.max(filtered_power):.2f} dB")

            # Identify where the power exceeds the threshold
            above_thresh = filtered_power > threshold_db
            min_duration_frames = int(0.03 * sr / hop_length)

            peaks, props = find_peaks(
                filtered_power,
                height=threshold_db,
                distance=int(0.03 * sr / hop_length),
                width=2,
            )
            logger.info(f"Detected {len(peaks)} peaks above threshold")

            # Step 1: Identify segments of the signal above the threshold
            segments = []
            count = 0
            start_idx = None

            for i, is_loud in enumerate(above_thresh):
                if is_loud:
                    if count == 0:
                        start_idx = i
                    count += 1
                else:
                    if count >= min_duration_frames:
                        segments.append((start_idx, i - 1))
                    count = 0

            if count >= min_duration_frames:
                segments.append((start_idx, len(above_thresh) - 1))

            # Step 2: Validate segments by checking for peaks within them
            validated_segments = []
            for start, end in segments:
                # Check if there's a peak within the segment
                if any((peak >= start and peak <= end) for peak in peaks):
                    validated_segments.append((start, end))

            # Step 3: Find the segment with the highest mean power
            best_segment = None
            best_power = -np.inf
            for start, end in validated_segments:
                segment_power = filtered_power[start : end + 1].mean()
                if segment_power > best_power:
                    best_power = segment_power
                    best_segment = (start, end)

            # if no segments were found, skip the spectrogram generation
            if best_segment is None:
                if filtered_only:
                    logger.info(
                        f"No significant segment in {filename}, spectrogram not generated."
                    )
                    return
                else:
                    logger.info(
                        f"No significant segment in {filename}, generating full spectrogram."
                    )
                    y_segment = y
                    start_time = 0
            else:
                start_frame, end_frame = best_segment
                start_time = start_frame * hop_length / sr
                end_time = end_frame * hop_length / sr
                logger.info(
                    f"Most significant segment in {filename}: "
                    f"from {start_time:.2f}s to {end_time:.2f}s "
                    f"(Total time : {end_time - start_time:.2f}s, mean power : {best_power:.2f} dB)"
                )

                if filtered_only and (len(y) / sr) >= 10:
                    y_segment = y[
                        int((start_time - 1) * sr) : int((start_time + 9) * sr)
                    ]
                else:
                    y_segment = y
                    start_time = 0

            # If the segment is empty, skip the spectrogram generation
            if len(y_segment) == 0:
                logger.warning(
                    f"Empty segment, unable to generate image for {filename}"
                )
                return

            # Compute the STFT of the segment to generate the spectrogram
            S = np.abs(librosa.stft(y_segment, n_fft=n_fft, hop_length=hop_length))
            S_dB = librosa.amplitude_to_db(S, ref=np.max)

            # Generate the spectrogram plot
            plt.figure(figsize=(10, 4))
            librosa.display.specshow(
                S_dB,
                sr=sr,
                hop_length=hop_length,
                x_axis="time",
                y_axis="linear",
                x_coords=np.arange(S_dB.shape[1]) * hop_length / sr + start_time,
            )
            plt.ylim(freq_min, freq_max)

            # Set labels for the axes
            plt.ylabel("Frequency (Hz)")  # Label for the y-axis
            plt.xlabel("Time (s)")  # Label for the x-axis
            plt.colorbar(format="%+2.0f dB")
            plt.title(f"Spectrogram - {filename}")
            plt.tight_layout()

            # Save the spectrogram as an image
            image_name = os.path.splitext(filename)[0] + ".png"
            image_path = os.path.join(IMG_DIR, image_name)
            plt.savefig(image_path)
            plt.close()
            File.objects.filter(link=filename).update(spectrogram_image=image_path)
            logger.info(f"Spectrogram saved: {image_path}")

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
