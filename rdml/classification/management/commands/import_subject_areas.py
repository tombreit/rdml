import csv
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from rdml.classification.models import CVSubjectArea

class Command(BaseCommand):
    help = 'CSV-Import: Populates SubjectArea model from CSV file data.'

    def add_arguments(self, parser):
        parser.add_argument('file')

    def handle(self, *args, **options):
        file = options['file']
        print(f"{file=}")

        target_model = CVSubjectArea

        with open(file) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                print(f'\t{row["CODE"]}: {row["NAME_EN"]} - {row["NAME_DE"]}')

                obj = target_model(
                    code=row["CODE"],
                    name_en=row["NAME_EN"],
                    name_de=row["NAME_DE"],
                    slug=slugify(row["NAME_EN"]),
                )
                obj.save()

            self.stdout.write(self.style.SUCCESS("Imported csv data!"))
