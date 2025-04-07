import logging
import requests
from django.core.management.base import BaseCommand
from urllib.parse import urlparse
from mousetube_api.models import File

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Check for dead links in mousetube files"

    def handle(self, *args, **options):
        logger.info("Starting dead link check...")

        files = File.objects.exclude(link_file__isnull=True).exclude(link_file="")

        for f in files:
            url = f.link_file
            parsed = urlparse(url)

            if parsed.hostname in ["localhost", "127.0.0.1"]:
                logger.info(f"Skipping local link: {url}")
                continue

            try:
                response = requests.head(url, allow_redirects=True, timeout=5)
                link_alive = response.status_code < 400
            except requests.RequestException as e:
                logger.error(f"BROKEN: {url} (Exception: {e})")
                link_alive = False

            if link_alive:
                logger.info(f"OK: {url}")
                if f.is_dead_link:
                    f.is_dead_link = False
                    f.save()
            else:
                logger.error(f"BROKEN: {url}")
                if not f.is_dead_link:
                    f.is_dead_link = True
                    f.save()

        logger.info("Dead link check finished.")