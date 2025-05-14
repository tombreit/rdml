# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2


from django.contrib.messages.storage.fallback import FallbackStorage
from itertools import chain


class DedupMessageMixin:
    """
    A mixin to prevent duplicate messages from being added to the message queue.
    """

    def add(self, level, message, extra_tags=""):
        # Messages loaded from the previous request and messages queued in the current request
        # _loaded_messages should be available (e.g. as an empty list if none were loaded)
        # in standard storage backends after messages are accessed.
        existing_messages = chain(getattr(self, "_loaded_messages", []), self._queued_messages)
        for m in existing_messages:
            if m.message == message and m.level == level:
                return  # Don't add if duplicate

        return super().add(level, message, extra_tags)


class DedupSessionStorage(DedupMessageMixin, FallbackStorage):
    pass
