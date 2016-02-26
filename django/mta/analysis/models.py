from __future__ import unicode_literals

from django.db import models


class Stats(models.Model):

    datetime = models.DateTimeField(blank=True, null=True)
    control_area = models.CharField(max_length=200, null=True)
    created_by_human = models.BooleanField()

    csv_row = models.IntegerField(default=0, null=True)
    file_name = models.CharField(max_length=200, blank=True, null=True)

    date = models.DateTimeField(null=True)
    description = models.CharField(max_length=200, null=True)
    division = models.CharField(max_length=200, null=True)
    interval = models.IntegerField(default=0, null=True)
    line_name = models.CharField(max_length=200, null=True)
    odometer_entries = models.BigIntegerField(default=0, null=True)
    odometer_exits = models.BigIntegerField(default=0, null=True)
    entries = models.IntegerField(default=0, blank=True, null=True)
    exits = models.IntegerField(default=0, blank=True, null=True)
    net_time = models.IntegerField(default=0, blank=True, null=True)
    net_flow = models.IntegerField(default=0, blank=True, null=True)
    cummulative_flow = models.IntegerField(default=0, blank=True, null=True)
    remote_unit = models.CharField(max_length=200, null=True)
    scp = models.CharField(max_length=200, null=True)
    station = models.CharField(max_length=200, null=True)

    minutes = models.IntegerField(default=0, null=True)
