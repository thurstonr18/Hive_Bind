from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords
import os
from django.utils import timezone


status_choices = (
	('1', 'Online'),
	('2', 'Offline'),
	('3', 'Unknown')
	)


class SoftwareGroup(models.Model):
	name  = models.CharField(max_length=200, blank=True, null=True)
	version  = models.CharField(max_length=200, blank=True, null=True)
	assigned = models.BooleanField(null=True, default=False)
	deploying = models.BooleanField(null=True, default=False)
	destination = models.CharField(max_length=1000, blank=False, null=True)
	uploaded = models.DateTimeField(null=True, default=timezone.now, blank=True)
	software = models.FileField(upload_to='Hive/software/IoT/', blank=True)
	devices = models.ManyToManyField('PIoT', blank=True)
	devices_deploying = models.ManyToManyField('PIoT', related_name='currently_deploying', blank=True)
	upload_history = HistoricalRecords(cascade_delete_history=True)


	def filename(self):
		if self.software.name:
			name = os.path.basename(self.software.name)
			return name
		else:
			return 'No software has been uploaded!\nGo upload some <a href="/software/">here</a>'

	def __str__(self):
		return self.name

#

class PIoT(models.Model):
	friendly_name = models.CharField(max_length=200, blank=True, null=True)
	operating_system = models.CharField(max_length=100, blank=True, null=True)
	vpnaddress = models.CharField(max_length=200, blank=True, null=True)
	identity = models.CharField(max_length=200, blank=True, null=True)
	identity2 = models.CharField(max_length=200, blank=True, null=True)
	mac = models.CharField(max_length=17, blank=True, null=True)
	mac2 = models.CharField(max_length=17, blank=True, null=True)
	online = models.CharField(choices=status_choices, max_length=25, null=True, default='3')

	nic = models.CharField(max_length=25, blank=True, null=True)
	nic2 = models.CharField(max_length=25, blank=True, null=True)
	gputemp = models.CharField(max_length=25, blank=True, null=True)
	cputemp = models.CharField(max_length=25, blank=True, null=True)
	cpu_usage = models.CharField(max_length=25, blank=True, null=True)
	memory = models.CharField(max_length=30, blank=True, null=True)
	voltage = models.CharField(max_length=25, blank=True, null=True)

	sgroup = models.ForeignKey(SoftwareGroup, related_name='mysoftware', on_delete=models.SET_NULL, null=True, blank=True)

	check_in = models.DateTimeField(null=True, default=timezone.now, blank=True)
	device_history = HistoricalRecords(cascade_delete_history=True)

	localdevices = models.TextField(blank=True, null=True)
	upspeed = models.CharField(max_length=6, blank=True, null=True)
	downspeed = models.CharField(max_length=6, blank=True, null=True)

	deploying = models.BooleanField(null=True, default=False)

	def __str__(self):
		if self.identity:
			return "{} - {} - {}".format(self.friendly_name, self.mac, self.identity)
		else:
			return "{} - {} - {}".format(self.friendly_name, self.mac2, self.identity2)

	def save(self, *args, **kwargs):
		self.check_in = timezone.now()
		super(PIoT, self).save(*args, **kwargs)










