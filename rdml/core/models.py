# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import uuid
from django.db import models


class SingletonBaseModel(models.Model):
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        abstract = True


class TimeStampedBaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDBaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True
