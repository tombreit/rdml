# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import csv
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.apps import apps
from rdml.core.helpers import get_orderable_representation
from rdml.classification.abstracts import CVGesisBaseModel


class Command(BaseCommand):
    help = "CSV-Import: Populates GESIS-compliant classifikation models from CSV file data."

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Django model classname")
        parser.add_argument("file", type=str, help='CSV file. Expects column headers "code", "name_de", "name_en".')

    def handle(self, *args, **options):
        file = options["file"]
        target_model_name = options["model"]

        # Get possible model classes that are subclasses of CVGesisBaseModel
        available_gesis_models = [model.__name__ for model in apps.get_models() if issubclass(model, CVGesisBaseModel)]
        _available_models_str = "\n".join(f"- {model}" for model in available_gesis_models)
        available_gesis_models_msg = f"Available GESIS models:\n{_available_models_str}"

        try:
            CVClass = apps.get_model(app_label="classification", model_name=target_model_name)
        except LookupError:
            self.stderr.write(self.style.ERROR(f"Model {target_model_name} not found."))
            self.stderr.write(self.style.ERROR(available_gesis_models_msg))
            return

        if not CVClass:
            self.stderr.write(self.style.ERROR(f"Model {target_model_name} not found."))
            self.stderr.write(self.style.ERROR(available_gesis_models_msg))
            return
        if not issubclass(CVClass, CVGesisBaseModel):
            self.stderr.write(self.style.ERROR(f"Model {target_model_name} is not a subclass of GVGesisBaseModel."))
            self.stderr.write(self.style.ERROR(available_gesis_models_msg))
            return

        print(f"Started importing data from {file} in {CVClass=}...")

        fieldnames = ["code", "name_de", "name_en"]

        objs = []

        with open(file) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=";", fieldnames=fieldnames)
            _first_line = next(csv_reader)
            _header_line = next(csv_reader)
            for row in csv_reader:
                name_de = row["name_de"]
                name_en = row["name_en"]

                code = row["code"]
                position = get_orderable_representation(code)

                obj = CVClass(
                    code=code,
                    position=position,
                    name_de=name_de,
                    name_en=name_en,
                    slug=slugify(name_en),
                )
                objs.append(obj)

            self.stdout.write(self.style.SUCCESS(f"Imported csv data for {CVClass}"))
