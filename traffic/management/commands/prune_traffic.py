from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from traffic.models import Visit


class Command(BaseCommand):
    help = "Delete visitor analytics older than 180 days; keep campaign links and leads."

    def handle(self, *args, **options):
        count, _ = Visit.objects.filter(started_at__lt=timezone.now() - timedelta(days=180)).delete()
        self.stdout.write(f"Deleted expired analytics rows: {count}")
