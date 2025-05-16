# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2


from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from rdml.core.helpers import linkchecker


class ResearchResourceAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        # Get all URLField fields from the model
        url_fields = [field for field in self.Meta.model._meta.get_fields() if isinstance(field, models.URLField)]

        # Check each URL field
        for field in url_fields:
            url_value = cleaned_data.get(field.name)
            if url_value:
                if not linkchecker(url_value):
                    self.add_error(field.name, ValidationError(f"The URL `{url_value}` appears to be unreachable."))

        return cleaned_data
