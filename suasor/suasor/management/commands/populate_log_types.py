#-- Populate table "log" with different log types.
#INSERT INTO log_type (name) VALUES ('ERROR');
#INSERT INTO log_type (name) VALUES ('INFO');
#INSERT INTO log_type (name) VALUES ('DEBUG');
#INSERT INTO log_type (name) VALUES ('WARNING');

from django.core.management.base import BaseCommand
from suasor.models import LogType


class Command(BaseCommand):
	def _create_tags(self):
		type = LogType(name='ERROR')
		type.save()

		type = LogType(name='INFO')
		type.save()

		type = LogType(name='DEBUG')
		type.save()

		type = LogType(name='WARNING')
		type.save()

	def handle(self, *args, **options):
		self._create_tags()
