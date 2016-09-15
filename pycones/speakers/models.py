# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from markupfield.fields import MarkupField


@python_2_unicode_compatible
class Speaker(models.Model):

    SESSION_COUNT_CHOICES = [
        (1, "One"),
        (2, "Two")
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, related_name="speaker_profile")
    name = models.CharField(max_length=100, help_text=("As you would like it to appear in the "
                                                       "conference program."))
    biography = MarkupField(
        blank=True,
        default="",
        default_markup_type='markdown',
        help_text=("A little bit about you.  Edit using "
                   "<a href='http://warpedvisions.org/projects/"
                   "markdown-cheat-sheet/target='_blank'>"
                   "Markdown</a>.")
    )
    photo = models.ImageField(upload_to="speaker_photos", blank=True)
    annotation = models.TextField()  # staff only
    invite_email = models.CharField(max_length=200, unique=True, null=True, db_index=True)
    invite_token = models.CharField(max_length=40, db_index=True)
    created = models.DateTimeField(
        default=datetime.datetime.now,
        editable=False
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.user:
            return self.name
        else:
            return "?"

    # def get_absolute_url(self):
    #    return reverse("speaker_edit")

    @property
    def email(self):
        if self.user is not None:
            return self.user.email
        else:
            return self.invite_email

    @property
    def all_presentations(self):
        presentations = []
        if self.presentations:
            for p in self.presentations.all():
                presentations.append(p)
            for p in self.copresentations.all():
                presentations.append(p)
        return presentations

    def has_biography(self):
        return bool(self.biography.raw)

    def get_api_id(self):
        return "S{:05d}".format(self.pk)
