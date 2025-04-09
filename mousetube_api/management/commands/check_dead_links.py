import logging
import requests
import time
from django.core.management.base import BaseCommand
from urllib.parse import urlparse
from mousetube_api.models import File

logger = logging.getLogger('check_dead_links')

class Command(BaseCommand):
    help = "Check for dead links in mousetube files"

    def handle(self, *args, **options):
        logger.info("Starting dead link check...")

        files = File.objects.exclude(link_file__isnull=True).exclude(link_file="")

        for file in files:
            url = file.link_file
            parsed = urlparse(url)

            # Check if the URL is valid
            if not url.startswith(("http://", "https://")):
                logger.error(f"Invalid URL format: {url}")
                continue

            # Skip local links (localhost, 127.0.0.1)
            if parsed.hostname in ["localhost", "127.0.0.1"]:
                logger.info(f"Skipping local link: {url}")
                continue

            try:
                # Send a HEAD request to avoid downloading the entire file
                time.sleep(1)  # Sleep for 1 second to avoid overwhelming the server
                
                # Check if the URL is reachable
                # Use a timeout to avoid hanging indefinitely
                # Use allow_redirects=True to follow redirects
                response = requests.head(url, allow_redirects=True, timeout=5)
                link_alive = response.status_code < 400
                if response.status_code == 429:
                    logger.warning(f"Rate limite reached with status code {response.status_code}: {url}")
                    continue
            except requests.RequestException as e:
                # Log broken links
                logger.error(f"BROKEN: {url} (Exception: {e})")
                link_alive = False

            # If the link is alive
            if link_alive:
                logger.info(f"OK: {url} {response.status_code}")
                if not file.is_valid_link:
                    file.is_valid_link = True
                    file.save()
            else:
                # If the link is dead
                logger.error(f"BROKEN: {url} {response.status_code}")
                if file.is_valid_link:
                    file.is_valid_link = False
                    file.save()

        files = File.objects.exclude(link_file__isnull=True).exclude(link_file="")
        valid_files = files.filter(is_valid_link=True)
        invalid_files = files.filter(is_valid_link=False)
        logger.info(f"Total files: {files.count()}")
        logger.info(f"Valid files: {valid_files.count()}")
        logger.info(f"Invalid files: {invalid_files.count()}")
        logger.info("Dead link check finished.")