# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import csv
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.apps import apps


class Command(BaseCommand):
    help = "CSV-Import: Populates DDI-compliant classifikation models from CSV file data."

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Django model classname")
        parser.add_argument(
            "file",
            type=str,
            help="CSV file. Must be converted from upstream https://ddialliance.org/controlled-vocabularies Excel file to csv first.",
        )

    def handle(self, *args, **options):
        file = options["file"]
        target_model_name = options["model"]
        CVClass = apps.get_model(app_label="classification", model_name=target_model_name)

        print(f"Started importing data from {file} in {CVClass=}...")

        fieldnames = ["Code", "Term", "Definition"]

        with open(file) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=";", fieldnames=fieldnames)
            _first_line = next(csv_reader)
            _header_line = next(csv_reader)
            for row in csv_reader:
                print(row)
                print(f"\t{row['Code']}: {row['Term']} - {row['Definition']}")

                obj = CVClass(
                    code=row["Code"],
                    name_en=row["Term"],
                    slug=slugify(row["Term"]),
                    definition=row["Definition"],
                )
                obj.save()

            self.stdout.write(self.style.SUCCESS(f"Imported csv data for {CVClass}"))
