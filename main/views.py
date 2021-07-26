from django.shortcuts import render
import subprocess
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django_user_agents.utils import get_user_agent
from django.template.loader import render_to_string
from django.template import RequestContext
from django.shortcuts import redirect
from django.db.models.signals import pre_save
from django.utils.crypto import get_random_string
from django.contrib.staticfiles.urls import static
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone
from django.db.models import F
import os
import re
import time 
import shutil
import json
import mimetypes
from datetime import datetime
from .models import PIoT, SoftwareGroup
from .forms import PIoTForm, SoftwareForm, PIoTUpdateForm, SoftwareUpdateForm, SoftwareEditForm, command_form
from bootstrap_modal_forms.generic import BSModalUpdateView
from django.views.generic.edit import UpdateView
from django.http import JsonResponse
from django.template.loader import render_to_string
import shutil


now = datetime.now()



def hardwares(request):
    data = dict()
    if request.method == 'GET':
        hw = PIoT.objects.all()
        # asyncSettings.dataKey = 'table'
        data['table'] = render_to_string(
            '_devices_table.html',
            {'hw': hw},
            request=request
        )
        return JsonResponse(data)

def softwares(request):
    data = dict()
    if request.method == 'GET':
        sw = SoftwareGroup.objects.all()
        # asyncSettings.dataKey = 'table'
        data['table'] = render_to_string(
            '_software_table.html',
            {'sw': sw},
            request=request
        )
        return JsonResponse(data)

def vpn_list(request):
	if request.method == 'GET':
		vpnlist = []
		acs = PIoT.objects.all()
		for a in acs:
			vpnlist.append(a.vpnaddress)

	return render(request, 'vpn_list.html', context={'vpnlist': acs})


def post_device(request):
	if request.method == 'GET':
		form = PIoTForm()

		return render(request, 'post_device.html', context={'form': form})
	else:
		print('POST')
		form = PIoTForm(request.POST)
		if form.is_valid():
			fname = form.cleaned_data['friendly_name']
			operating_system = form.cleaned_data['operating_system']
			vpnaddress = form.cleaned_data['vpnaddress']
			identity = form.cleaned_data['identity']
			identity2 = form.cleaned_data['identity2']
			mac = form.cleaned_data['mac']
			mac2 = form.cleaned_data['mac2']
			online = form.cleaned_data['online']
			nic = form.cleaned_data['nic']
			nic2 = form.cleaned_data['nic2']
			gputemp = form.cleaned_data['gputemp']
			cputemp = form.cleaned_data['cputemp']
			memory = form.cleaned_data['memory']
			voltage = form.cleaned_data['voltage']
			cpu_usage = form.cleaned_data['cpu_usage']
			localdevices = form.cleaned_data['localdevices']
			upspeed = form.cleaned_data['upspeed']
			downspeed = form.cleaned_data['downspeed']

			sgroup = form.cleaned_data['sgroup']
			if PIoT.objects.filter(identity=identity, mac=mac).exists():
				for obj in PIoT.objects.filter(identity=identity, mac=mac):
					mid = PIoT.objects.get(id=obj.id)
					pid = obj.id
					obj.friendly_name = fname
					obj.operating_system = operating_system
					obj.vpnaddress = vpnaddress
					obj.identity = identity
					obj.identity2 = identity2
					obj.mac = mac
					obj.mac2 = mac2
					obj.online = online
					obj.nic = nic
					obj.nic2 = nic2
					obj.gputemp = gputemp
					obj.cputemp = cputemp
					obj.memory = memory
					obj.voltage = voltage
					obj.cpu_usage = cpu_usage
					obj.sgroup = sgroup
					obj.localdevices = localdevices
					obj.upspeed = upspeed
					obj.downspeed = downspeed
					obj.save()

				if sgroup is not None:
					a = SoftwareGroup.objects.filter(name=sgroup)
					for s in a:
						s.devices.add(mid)

				else:
					a = SoftwareGroup.objects.filter(name=sgroup)
					for s in a:
						s.devices.remove(mid)

				return HttpResponseRedirect(reverse('update_hardware', kwargs={'pk': pid}))
			else:
				pc = PIoT.objects.create(friendly_name=fname, vpnaddress=vpnaddress, identity=identity, identity2=identity2, mac=mac, mac2=mac2, online=online, nic=nic, nic2=nic2, gputemp=gputemp, cputemp=cputemp, memory=memory, cpu_usage=cpu_usage, voltage=voltage, sgroup=sgroup, localdevices=localdevices, upspeed=upspeed, downspeed=downspeed, operating_system=operating_system)

				if sgroup is not None:
					a = SoftwareGroup.objects.filter(name=sgroup)
					for s in a:
						s.devices.add(pc)
				else:
					pass

				return HttpResponseRedirect(reverse('update_hardware', kwargs={'pk': pc.id}))

		else:
			print(form.errors)


		return HttpResponseRedirect('/post_device/')




class AboutView(TemplateView):
	def get(self, request):
		if request.method == 'GET':
			user_agent = get_user_agent(request)
			if user_agent.is_mobile:
				return render(request, 'mobileabout.html')
			else:
				return render(request, 'about.html')



class PotPi(TemplateView):
	def get(self, request, pk):
		if request.method == 'GET':
			mydevice = PIoT.objects.filter(pk=pk)
			labels = []
			dlabels = []
			alltimelabels = []
			cpu = []
			dcpu = []
			dcputemp = []
			dgputemp = []
			dmemory = []
			cputemp = []
			gputemp = []
			memory = []
			voltage = []
			uloaddaily = []
			dloaddaily = []
			uload = []
			dload = []

			hw = PIoT.device_history.filter(id=pk, operating_system__contains='Linux').order_by('check_in')

			chw = PIoT.objects.filter(id=pk, operating_system__contains='Linux').order_by('check_in')
			chww = PIoT.objects.filter(id=pk).order_by('check_in')

			win = PIoT.objects.filter(id=pk, operating_system__contains='Windows').order_by('check_in')
			winh = PIoT.device_history.filter(id=pk, operating_system__contains='Windows').order_by('check_in')

			for os in chww:
				myos = os.operating_system


			try:
				for obj in hw:
					alltimelabels.append(obj.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uload.append(obj.upspeed)
					dload.append(obj.downspeed)
					cpu.append(obj.cpu_usage)
					gputemp.append(obj.gputemp.replace('°', '').replace('F', '').replace('\'', ''))
					cputemp.append(obj.cputemp.replace('°', '').replace('F', '').replace('\'', ''))
					memory.append(obj.memory)
					voltage.append(obj.voltage)


				for i in PIoT.device_history.filter(id=pk, operating_system__contains='Linux', check_in__contains=now.strftime("%Y-%m-%d")).order_by('check_in'):

					dlabels.append(i.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uloaddaily.append(i.upspeed)
					dloaddaily.append(i.downspeed)
					dcpu.append(i.cpu_usage)
					dgputemp.append(i.gputemp.replace('°', '').replace('F', '').replace('\'', ''))
					dcputemp.append(i.cputemp.replace('°', '').replace('F', '').replace('\'', ''))
					dmemory.append(i.memory)

					voltage.append(i.voltage)
			except AttributeError:
				for i in chw:
					cpu.append(i.cpu_usage)
					cputemp.append(i.cputemp.replace('°', '').replace('F', '').replace('\'', ''))
					gputemp.append(i.gputemp.replace('°', '').replace('F', '').replace('\'', ''))
					memory.append(i.memory)

			try:
				for obj in winh:
					print(obj.check_in)
					alltimelabels.append(obj.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uload.append(obj.upspeed)
					dload.append(obj.downspeed)
					cpu.append(obj.cpu_usage)
					memory.append(obj.memory)


				for i in PIoT.device_history.filter(id=pk, operating_system__contains='Windows', check_in__contains=now.strftime("%Y-%m-%d")).order_by('check_in'):

					dlabels.append(i.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uloaddaily.append(i.upspeed)
					dloaddaily.append(i.downspeed)
					dcpu.append(i.cpu_usage)
					dmemory.append(i.memory)


			except AttributeError:
				for i in win:

					cpu.append(i.cpu_usage)
					memory.append(i.memory)

			dailystuff = zip(dlabels, uloaddaily, dloaddaily)
			#print(list(dailystuff))
			ldevicename = []
			ldevicemac = []
			ldeviceip = []
			for a in mydevice:
				mlist = re.findall(r'.*,', str(a.localdevices))
			for item in mlist:
				r1 = re.search(r'(.*,\s)(\w*:.*,)(.*,)', str(item))
				ldevicename.append(str(r1.group(1)).replace(',', ''))
				ldevicemac.append(str(r1.group(2)).replace(',', ''))
				ldeviceip.append(str(r1.group(3)).replace(',', ''))


			mlocal = zip(ldevicename, ldevicemac, ldeviceip)
			masterlocal = list(mlocal)


		user_agent = get_user_agent(request)
		if user_agent.is_mobile:
			return render(request, 'mobilepi_side.html', context={"mydevice": mydevice, 'mlocal': masterlocal, 'labels': labels, 'alltimelabels': alltimelabels, 'uloaddaily': uloaddaily, 'dloaddaily': dloaddaily, 'dlabels': dlabels, 'cpu': cpu, 'cputemp': cputemp, 'gputemp': gputemp, 'memory': memory, 'dcpu': dcpu, 'dmemory': dmemory, 'dcputemp': dcputemp, 'dgputemp': dgputemp, 'dload': dload, 'uload': uload, 'myos': myos})
		else:
			return render(request, 'pi_side.html', context={"mydevice": mydevice, 'mlocal': masterlocal, 'labels': labels, 'alltimelabels': alltimelabels, 'uloaddaily': uloaddaily, 'dloaddaily': dloaddaily, 'dlabels': dlabels, 'cpu': cpu, 'cputemp': cputemp, 'gputemp': gputemp, 'memory': memory, 'dcpu': dcpu, 'dmemory': dmemory, 'dcputemp': dcputemp, 'dgputemp': dgputemp, 'dload': dload, 'uload': uload, 'myos': myos})


def call(request):
	call_form = command_form(request.POST)

	if request.is_ajax():
		print(request.POST)
		cmd = request.POST.get('cmd')
		p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = p1.communicate()
		output = out.decode('utf8')

		response_data = {'output_call': output}
		return HttpResponse(
			json.dumps(response_data),
			content_type="application/json"
		)

class IndexView(TemplateView):
	def get(self, request):
		if request.method == 'GET':
			my_devices = PIoT.objects.all()
			deviceson = PIoT.objects.filter(online='1')
			devicesoff = PIoT.objects.filter(online='2')
			software = SoftwareGroup.objects.all()
			deviceswindows = PIoT.objects.filter(operating_system__contains='Windows')
			devicesraspi1 = PIoT.objects.filter(operating_system__contains='Debian')
			devicesraspi2 = PIoT.objects.filter(operating_system__contains='Raspbian')
			devicesubuntu = PIoT.objects.filter(operating_system__contains='Ubuntu')
			try:
				lastsoft = SoftwareGroup.objects.latest('software')
				lsoft = settings.MEDIA_ROOT + str(lastsoft.software).replace('Hive/', '')

				softname = lastsoft.software
				b = lastsoft.software.path

				r1 = re.sub(r'_[^._]+(?=[^_]*$)', '', str(b))

				b2 = settings.MEDIA_ROOT + str()

				f =  open(b, encoding='utf8')
				lines = f.read()
				f.close()
			except (ObjectDoesNotExist, UnicodeDecodeError):
				lines = ''
				lastsoft = ''
				lsoft = ''
				b = ''
				softname = ''
			

			user_agent = get_user_agent(request)
			if user_agent.is_mobile:
				return render(request, 'mobileindex.html', context={'my_devices': my_devices, 'deviceson': deviceson, 'devicesoff': devicesoff, 'software': software, 'lastsoft': lines, 'spath': b, 'lsoft': lsoft, 'softname': softname, 'lspk': lastsoft, 'deviceswindows': len(deviceswindows), 'devicesraspi': len(devicesraspi1) + len(devicesraspi2), 'devicesubuntu': len(devicesubuntu)})
			else:
				return render(request, 'index.html', context={'my_devices': my_devices, 'deviceson': deviceson, 'devicesoff': devicesoff, 'software': software, 'lastsoft': lines, 'spath': b, 'lsoft': lsoft, 'softname': softname, 'lspk': lastsoft, 'deviceswindows': len(deviceswindows), 'devicesraspi': len(devicesraspi1) + len(devicesraspi2), 'devicesubuntu': len(devicesubuntu)})

	def post(self, request):
		if request.method == 'POST':
			fl_path = settings.MEDIA_ROOT + 'software/add_to_hive.py'
			filename = 'add_to_hive.py'
			print(fl_path)

			fl = open(fl_path, 'r')
			mime_type, _ = mimetypes.guess_type(fl_path)
			response = HttpResponse(fl, content_type=mime_type)
			response['Content-Disposition'] = "attachment; filename=%s" % filename
			return response


class HardwareView(TemplateView):
	def get(self, request):
		if request.method == 'GET':

			deviceson = PIoT.objects.filter(online=True)
			devicesoff = PIoT.objects.filter(online=False)
			devices = PIoT.objects.all().order_by(F('sgroup').desc(nulls_last=True))

			software = SoftwareGroup.objects.all()

			try:
				for a in software:
					obj = SoftwareGroup.objects.get(id=a.id)
					device_num = []
					software_pk = []
					try:
						for b in PIoT.objects.filter(sgroup=obj):
							device_num.append(b.friendly_name)
							c = SoftwareGroup.objects.filter(devices__id=b.pk)



					except UnboundLocalError:
						pass

			except:
				pass

			try:
				devicenum = len(device_num)
				print(devicenum)
			except UnboundLocalError:
				devicenum = 0
			form = PIoTForm()
			user_agent = get_user_agent(request)
			if user_agent.is_mobile:
				return render(request, 'mobilehardware.html', context={'form': form, 'hw': devices, 'sw': software, 'devicenum': devicenum, 'deviceson': deviceson, 'devicesoff': devicesoff})
			else:
				return render(request, 'hardware.html', context={'form': form, 'hw': devices, 'sw': software, 'devicenum': devicenum, 'deviceson': deviceson, 'devicesoff': devicesoff})


	def post(self, request):
		if request.method == 'POST':

			if 'addNewHardware' in request.POST:
				form = PIoTForm(request.POST)
				if form.is_valid():
					fname = form.cleaned_data['friendly_name']
					operating_system = form.cleaned_data['operating_system']
					identity = form.cleaned_data['identity']
					mac = form.cleaned_data['mac']
					online = form.cleaned_data['online']
					sgroup = form.cleaned_data['sgroup']
					if PIoT.objects.filter(identity=identity, mac=mac).exists():
						for obj in PIoT.objects.filter(identity=identity, mac=mac):
							mid = PIoT.objects.get(id=obj.id)
							obj.friendly_name = fname
							obj.operating_system = operating_system
							obj.identity = identity
							obj.mac = mac
							obj.online = online
							obj.sgroup = sgroup
							obj.save()

						if sgroup is not None:
							a = SoftwareGroup.objects.filter(name=sgroup)
							for s in a:
								s.devices.add(mid)
								s.assigned = True


						else:
							a = SoftwareGroup.objects.filter(name=sgroup)
							for s in a:
								s.devices.remove(mid)
								s.assigned = False

					else:
						pc = PIoT.objects.create(friendly_name=fname, identity=identity, mac=mac, online=online, sgroup=sgroup)

						if sgroup is not None:
							a = SoftwareGroup.objects.filter(name=sgroup)
							for s in a:
								s.devices.add(pc)
						else:
							pass

				else:
					print(form.errors)

				return HttpResponseRedirect('/hardware/')

			elif 'deployHardware' in request.POST:
				devicepk = request.POST.get('deployHardware')
				thisd = PIoT.objects.filter(pk=devicepk)
				for i in thisd:
					sgrouppk = i.sgroup_id
					i.deploying = True
					i.save()

				initpath = settings.MEDIA_ROOT + 'software/Staging/' + str(sgrouppk) + '/'
				if os.path.isdir(initpath):
					pass
				else:
					os.makedirs(initpath)
					mysoft = SoftwareGroup.objects.filter(pk=sgrouppk)
					for a in mysoft:
						mysoftware = a.software
						b = mysoftware.path

					shutil.copy(b, initpath)


				return HttpResponseRedirect('/hardware/')

			elif 'downloadLinuxCall' in request.POST:
				linux = settings.MEDIA_ROOT + 'Hive/software/hiveservice.py'

				linux_filename = 'hiveservice.py'
				#print(linux)


				fl = open(linux, 'r')
				mime_type, _ = mimetypes.guess_type(linux)
				response = HttpResponse(fl, content_type=mime_type)
				response['Content-Disposition'] = "attachment; filename=%s" % linux_filename
				return response

			elif 'downloadWindowsCall' in request.POST:
				windows = settings.MEDIA_ROOT + 'Hive/software/HiveAgentWin.exe'

				windows_filename = 'HiveAgentWin.exe'

				fl = open(windows, 'rb')
				mime_type, _ = mimetypes.guess_type(windows)
				response = HttpResponse(fl, content_type=mime_type)
				response['Content-Disposition'] = "attachment; filename=%s" % windows_filename
				return response

			elif 'assignDevices' in request.POST:
				print(request.POST)
				checked = request.POST.get('assignDevices')
				pk = request.POST.getlist('fname')
				allsoft = SoftwareGroup.objects.all()
				for i in pk:
					sware = SoftwareGroup.objects.get(id=i)

					aa = PIoT.objects.get(id=checked)
					for instance in SoftwareGroup.objects.filter(pk=i):
						instance.devices.add(aa)
						instance.assigned = True
						instance.save()

				for item in PIoT.objects.filter(id=checked):
					print(checked)
					print(sware)
					item.sgroup = sware
					item.save()


			elif 'removeGroup' in request.POST:
				pk = request.POST.get('pk')
				for obj in PIoT.objects.filter(pk=pk):
					obj.sgroup = None
					obj.save()
				for instance in SoftwareGroup.objects.filter(devices=pk):
					instance.devices.remove(pk)
					instance.devices_deploying.remove(pk)

					if not instance.devices.all():
						instance.assigned = False
					instance.save()
			return HttpResponseRedirect('/hardware/')

class AutoPiStatusView(UpdateView):
	model = PIoT
	fields = ['online']
	template_name = 'autopistatus.html'

	def post(self, request, pk):
		if request.method == 'POST':
			form = PIoTUpdateForm(request.POST)
			if form.is_valid():
				print('valid')
				online = form.cleaned_data['online']

				if PIoT.objects.filter(pk=pk).exists():
					for a in PIoT.objects.filter(pk=pk):
						a.online = online
						a.save()
		return HttpResponseRedirect('/hardware/')

class AutoPiUpdateView(UpdateView):
	model = PIoT
	fields = ['online', 'vpnaddress', 'mac', 'mac2', 'identity', 'identity2', 'nic', 'nic2', 'gputemp', 'cputemp', 'memory', 'cpu_usage', 'voltage', 'localdevices', 'upspeed', 'downspeed', 'operating_system', 'check_in']
	template_name = 'autopiupdate.html'

	def post(self, request, pk):
		if request.method == 'POST':
			form = PIoTUpdateForm(request.POST, initial={'check_in': timezone.now()})
			if form.is_valid():

				vpnaddress = form.cleaned_data['vpnaddress']
				operating_system = form.cleaned_data['operating_system']
				mac = form.cleaned_data['mac']
				mac2 = form.cleaned_data['mac2']
				identity = form.cleaned_data['identity']
				identity2 = form.cleaned_data['identity2']
				online = form.cleaned_data['online']
				nic = form.cleaned_data['nic']
				nic2 = form.cleaned_data['nic2']
				gputemp = form.cleaned_data['gputemp']
				cputemp = form.cleaned_data['cputemp']
				memory = form.cleaned_data['memory']
				cpu_usage = form.cleaned_data['cpu_usage']
				voltage = form.cleaned_data['voltage']
				localdevices = form.cleaned_data['localdevices']
				upspeed = form.cleaned_data['upspeed']
				downspeed = form.cleaned_data['downspeed']

				for item in PIoT.objects.filter(pk=pk):
					item.vpnaddress = vpnaddress
					item.operating_system = operating_system
					item.online = online
					item.mac = mac
					item.mac2 = mac2
					item.identity = identity
					item.identity2 = identity2
					item.nic = nic
					item.nic2 = nic2
					item.gputemp = gputemp
					item.cputemp = cputemp
					item.memory = memory
					item.cpu_usage = cpu_usage
					item.voltage = voltage
					item.localdevices = localdevices
					item.upspeed = upspeed
					item.downspeed = downspeed
					item.check_in = str(timezone.now())

					item.save()

		return HttpResponseRedirect('/hardware/')


class PIoTUpdateView(BSModalUpdateView):
	model = PIoT
	template_name = 'update_hardware.html'
	form_class = PIoTUpdateForm
	success_message = 'Success: Device was updated.'
	success_url = reverse_lazy('index')


	def get(self, request, pk):
		if request.method == 'GET':
			for name in PIoT.objects.filter(pk=pk):
				friendly_name = name.friendly_name
			form = self.form_class(initial={'friendly_name': friendly_name})
			mydevice = PIoT.objects.filter(pk=pk)
			labels = []
			dlabels = []
			alltimelabels = []
			cpu = []
			dcpu = []
			dcputemp = []
			dgputemp = []
			dmemory = []
			cputemp = []
			gputemp = []
			memory = []
			voltage = []
			uloaddaily = []
			dloaddaily = []
			uload = []
			dload = []

			hw = PIoT.device_history.filter(id=pk, operating_system__contains='Linux').order_by('check_in')

			chw = PIoT.objects.filter(id=pk, operating_system__contains='Linux').order_by('check_in')
			chww = PIoT.objects.filter(id=pk)

			win = PIoT.objects.filter(id=pk, operating_system='Windows')
			winh = PIoT.device_history.filter(id=pk, operating_system='Windows')

			for os in chww:
				myos = os.operating_system

			try:
				for obj in hw:
					alltimelabels.append(obj.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uload.append(obj.upspeed)
					dload.append(obj.downspeed)
					cpu.append(obj.cpu_usage)
					gputemp.append(obj.gputemp.replace('°', '').replace('F', '').replace('\'', ''))
					cputemp.append(obj.cputemp.replace('°', '').replace('F', '').replace('\'', ''))
					memory.append(obj.memory)
					voltage.append(obj.voltage)


				for i in PIoT.device_history.filter(id=pk, operating_system__contains='Linux', check_in__contains=now.strftime("%Y-%m-%d")).order_by('check_in'):

					dlabels.append(i.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uloaddaily.append(i.upspeed)
					dloaddaily.append(i.downspeed)
					dcpu.append(i.cpu_usage)
					dgputemp.append(i.gputemp.replace('°', '').replace('F', '').replace('\'', ''))
					dcputemp.append(i.cputemp.replace('°', '').replace('F', '').replace('\'', ''))
					dmemory.append(i.memory)

					voltage.append(i.voltage)
			except AttributeError:
				for i in chw:
					cpu.append(i.cpu_usage)
					cputemp.append(i.cputemp.replace('°', '').replace('F', '').replace('\'', ''))
					gputemp.append(i.gputemp.replace('°', '').replace('F', '').replace('\'', ''))
					memory.append(i.memory)

			try:
				for obj in winh:
					alltimelabels.append(obj.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uload.append(obj.upspeed)
					dload.append(obj.downspeed)
					cpu.append(obj.cpu_usage)
					memory.append(obj.memory)


				for i in PIoT.device_history.filter(id=pk, operating_system__contains='Windows', check_in__contains=now.strftime("%Y-%m-%d")).order_by('check_in'):

					dlabels.append(i.check_in.strftime("%I:%M %p %m-%d-%Y"))
					uloaddaily.append(i.upspeed)
					dloaddaily.append(i.downspeed)
					dcpu.append(i.cpu_usage)
					dmemory.append(i.memory)


			except AttributeError:
				for i in win:
					cpu.append(i.cpu_usage)
					memory.append(i.memory)
		user_agent = get_user_agent(request)
		if user_agent.is_mobile:

			return render(request, 'mobileupdate_hardware.html', context={'labels': labels, 'cpu_usage': cpu, 'memory': memory, 'cputemp': cputemp, 'gputemp': gputemp, 'voltage': voltage, 'form': form, 'mydevice': chww})
		else:
			return render(request, 'update_hardware.html', context={'labels': labels, 'cpu_usage': cpu, 'memory': memory, 'cputemp': cputemp, 'gputemp': gputemp, 'voltage': voltage, 'form': form, 'mydevice': chww})

	def post(self, request, pk):
		if request.is_ajax():
			form = PIoTUpdateForm(request.POST, request.FILES)
			if form.is_valid():
				fname = form.cleaned_data['friendly_name']
				operating_system = form.cleaned_data['operating_system']
				vpnaddress = form.cleaned_data['vpnaddress']
				identity = form.cleaned_data['identity']
				identity2 = form.cleaned_data['identity2']
				mac = form.cleaned_data['mac']
				mac2 = form.cleaned_data['mac2']
				online = form.cleaned_data['online']
				nic = form.cleaned_data['nic']
				nic2 = form.cleaned_data['nic2']
				gputemp = form.cleaned_data['gputemp']
				cputemp = form.cleaned_data['cputemp']
				memory = form.cleaned_data['memory']
				cpu_usage = form.cleaned_data['cpu_usage']
				voltage = form.cleaned_data['voltage']
				localdevices = form.cleaned_data['localdevices']
				upspeed = form.cleaned_data['upspeed']
				downspeed = form.cleaned_data['downspeed']

				sgroup = form.cleaned_data['sgroup']
				if PIoT.objects.filter(identity=identity, mac=mac).exists():
					for obj in PIoT.objects.filter(identity=identity, mac=mac):
						obj.friendly_name = fname
						obj.operating_system = operating_system
						obj.vpnaddress = vpnaddress
						obj.identity = identity
						obj.identity2 = identity2
						obj.mac = mac
						obj.mac2 = mac2
						obj.online = online
						obj.nic = nic
						obj.nic2 = nic2
						obj.gputemp = gputemp
						obj.cputemp = cputemp
						obj.memory = memory
						obj.cpu_usage = cpu_usage
						obj.voltage = voltage
						obj.sgroup = sgroup
						obj.localdevices = localdevices
						obj.upspeed = upspeed
						obj.downspeed = downspeed
						obj.save()
						mid = PIoT.objects.get(id=obj.id)

					if sgroup is not None:
						print(sgroup)
						a = SoftwareGroup.objects.filter(name=sgroup)
						for s in a:
							s.devices.add(mid)

					else:
						if SoftwareGroup.objects.filter(devices=mid).exists():
							for s in SoftwareGroup.objects.filter(devices=mid):
								s.devices.remove(mid)
				else:
					pc = PIoT.objects.create(friendly_name=fname, vpnaddress=vpnaddress, identity=identity, identity2=identity2, online=online, mac=mac, mac2=mac2, nic=nic, nic2=nic2, gputemp=gputemp, cputemp=cputemp, memory=memory, cpu_usage=cpu_usage, voltage=voltage, sgroup=sgroup, localdevices=localdevices, upspeed=upspeed, downspeed=downspeed, operating_system=operating_system)

					if sgroup is not None:
						a = SoftwareGroup.objects.filter(name=sgroup)
						for s in a:
							s.devices.add(pc)
					else:
						if SoftwareGroup.objects.filter(devices=pc).exists():
							for s in SoftwareGroup.objects.filter(devices=pc):
								s.devices.remove(pc)
						else:
							pass

			else:
				print(form.errors)


			return HttpResponseRedirect('/hardware/')
		else:

			form = PIoTUpdateForm(request.POST, request.FILES)
			if form.is_valid():
				fname = form.cleaned_data['friendly_name']
				operating_system = form.cleaned_data['operating_system']
				vpnaddress = form.cleaned_data['vpnaddress']
				identity = form.cleaned_data['identity']
				identity2 = form.cleaned_data['identity2']
				mac = form.cleaned_data['mac']
				mac2 = form.cleaned_data['mac2']
				online = form.cleaned_data['online']
				nic = form.cleaned_data['nic']
				nic2 = form.cleaned_data['nic2']
				gputemp = form.cleaned_data['gputemp']
				cputemp = form.cleaned_data['cputemp']
				memory = form.cleaned_data['memory']
				cpu_usage = form.cleaned_data['cpu_usage']
				voltage = form.cleaned_data['voltage']
				localdevices = form.cleaned_data['localdevices']
				upspeed = form.cleaned_data['upspeed']
				downspeed = form.cleaned_data['downspeed']

				sgroup = form.cleaned_data['sgroup']
				if PIoT.objects.filter(identity=identity, mac=mac).exists():
					for obj in PIoT.objects.filter(identity=identity, mac=mac):
						obj.friendly_name = fname
						obj.operating_system = operating_system
						obj.vpnaddress = vpnaddress
						obj.identity = identity
						obj.identity2 = identity2
						obj.mac = mac
						obj.mac2 = mac2
						obj.online = online
						obj.nic = nic
						obj.nic2 = nic2
						obj.gputemp = gputemp
						obj.cputemp = cputemp
						obj.memory = memory
						obj.cpu_usage = cpu_usage
						obj.voltage = voltage
						obj.sgroup = sgroup
						obj.localdevices = localdevices
						obj.upspeed = upspeed
						obj.downspeed = downspeed
						obj.save()
						mid = PIoT.objects.get(id=obj.id)

					if sgroup is not None:
						print(sgroup)
						a = SoftwareGroup.objects.filter(name=sgroup)
						for s in a:
							s.devices.add(mid)

					else:
						if SoftwareGroup.objects.filter(devices=mid).exists():
							for s in SoftwareGroup.objects.filter(devices=mid):
								s.devices.remove(mid)
				else:
					pc = PIoT.objects.create(friendly_name=fname, vpnaddress=vpnaddress, identity=identity, identity2=identity2, online=online, mac=mac, mac2=mac2, nic=nic, nic2=nic2, gputemp=gputemp, cputemp=cputemp, memory=memory, cpu_usage=cpu_usage, voltage=voltage, sgroup=sgroup, localdevices=localdevices, upspeed=upspeed, downspeed=downspeed, operating_system=operating_system)

					if sgroup is not None:
						a = SoftwareGroup.objects.filter(name=sgroup)
						for s in a:
							s.devices.add(pc)
					else:
						if SoftwareGroup.objects.filter(devices=pc).exists():
							for s in SoftwareGroup.objects.filter(devices=pc):
								s.devices.remove(pc)
						else:
							pass

			else:
				print(form.errors)


			return HttpResponseRedirect('/hardware/')



class SoftwareView(TemplateView):
	def get(self, request):
		if request.method == 'GET':
			form = SoftwareForm()

			devices = PIoT.objects.all().order_by(F('sgroup').desc(nulls_last=True))
			unassigned_devices = PIoT.objects.filter(sgroup=None)
			software = SoftwareGroup.objects.all()

			if software:
				for b in software:
					if b.devices.all():
						b.assigned = True
						b.save()
					else:
						b.assigned = False
						b.save()
			try:
				for a in software:
					obj = SoftwareGroup.objects.get(id=a.id)


				device_num = []

				for b in PIoT.objects.filter(sgroup=obj):
					device_num.append(b.friendly_name)
				devicenum = len(device_num)
			except UnboundLocalError:
				devicenum = None


			groups = SoftwareGroup.objects.values_list('mysoftware', flat=True)
		user_agent = get_user_agent(request)
		if user_agent.is_mobile:
			return render(request, 'mobilesoftware_upload.html', context={'form': form, 'software': software, 'devicenum': devicenum, 'udevices': unassigned_devices})
		else:
			return render(request, 'software_upload.html', context={'form': form, 'software': software, 'devicenum': devicenum, 'udevices': unassigned_devices})

	def post(self, request):
		if request.method == 'POST':
			if 'addNewSoftware' in request.POST:
				form = SoftwareForm(request.POST, request.FILES)
				if form.is_valid():
					print('Valid')
					name = form.cleaned_data['name']
					version = form.cleaned_data['version']
					status = False
					destination = form.cleaned_data['destination']
					instance = SoftwareGroup(name=name, version=version, assigned=status, destination=destination, software=request.FILES['software'])
					instance.save()
				else:
					print(form.errors)
			elif 'assignDevices' in request.POST:

				sub_choices = []
				checked = request.POST.getlist('fname')
				pk = request.POST.get('assignDevices')
				sware = SoftwareGroup.objects.get(id=pk)
				for obj in checked:
					aa = PIoT.objects.get(id=obj)
					for instance in SoftwareGroup.objects.filter(pk=pk):
						instance.devices.add(aa)
						instance.assigned = True
						instance.save()
					for item in PIoT.objects.filter(id=obj):
						item.sgroup = sware
						item.save()

			elif 'masterPush' in request.POST:
				devicepk = request.POST.getlist('devicePK')
				softwarepk = request.POST.get('softwarePK')

				mysoft = SoftwareGroup.objects.filter(pk=softwarepk)
				for dpk in devicepk:
					mydevice = PIoT.objects.filter(pk=dpk)

				initpath = settings.MEDIA_ROOT + 'software/Staging/' + str(softwarepk) + '/'
				if os.path.isdir(initpath):
					shutil.rmtree(initpath)
					os.makedirs(initpath)
				else:
					os.makedirs(initpath)

				for a in mysoft:
					mysoftware = a.software
					b = mysoftware.path
					final_dest = a.destination


				attributed_devices = mysoft.values_list('devices__id', flat=True)
				for d in mydevice:
					d.deploying = True
					d.save()
				for s in mysoft:
					for ad in attributed_devices:
						s.devices_deploying.add(ad)
					s.deploying = True
					s.save()
				shutil.copy(b, initpath)



		return HttpResponseRedirect('/software/')



class Removal(TemplateView):
	def get(self, request, pk):
		if request.method == 'GET':
			devices = PIoT.objects.filter(pk=pk)
			return render(request, 'update_complete.html', context={'devices': devices})

	def post(self, request, pk):
		if request.method == 'POST':
			devicepk = request.POST.get('completedUpdates')
			a = SoftwareGroup.objects.filter(devices__id=devicepk)

			b = PIoT.objects.filter(pk=pk)
			for obj in b:
				sid = obj.sgroup_id
				obj.deploying = False
				obj.save()

			this_soft = SoftwareGroup.objects.filter(pk=sid)
			for c in this_soft:
				c.devices_deploying.remove(devicepk)
				if not c.devices_deploying.all():
					c.deploying = False
					c.save()
				else:
					pass

		return HttpResponseRedirect('/software/')



class Determination(TemplateView):
	def get(self, request):
		if request.method == 'GET':
			devices = PIoT.objects.all()
			groups = SoftwareGroup.objects.filter(deploying=True)
			glist = [] 

			for g in groups:

				for a in g.devices.all():

					filteredgroup = SoftwareGroup.objects.filter(devices=a)
					for b in filteredgroup:

						pk = b.pk
						dv = b.devices.filter(friendly_name=a.friendly_name)
						for i in dv:
							mydict = {
								"spk": pk,
								"dest": b.destination,
								"dpk":[
										{
											"pk": i.pk,
										}
									]
								}
							glist.append(mydict)
			

		try:
			return render(request, 'determination.html', context={'devices': devices, 'groups': groups, 'json': json.dumps(glist)})
		except AttributeError:
			return render(request, 'determination.html')

def hardware_determination(request, pk):
	if request.method == 'GET':
		devicepk = pk
		thisd = PIoT.objects.filter(pk=devicepk)
		for i in thisd:
			sgrouppk = i.sgroup_id
			if i.deploying == True:
				for dest in SoftwareGroup.objects.filter(pk=sgrouppk):
					destination = dest.destination
				glist = []

				mydict = {
					"spk": sgrouppk,
					"dest": destination,
					"dpk":[
							{
								"pk": devicepk,
							}
						]
					}
				glist.append(mydict)


		try:
			return render(request, 'hwdetermination.html', context={'json': json.dumps(glist)})
		except (AttributeError, UnboundLocalError):
			return render(request, 'hwdetermination.html')




def hardware_determination_removal(request, pk):
	if request.method == 'GET':
		devices = PIoT.objects.filter(pk=pk)
		return render(request, 'hwupdate_complete.html', context={'devices': devices})
	else:


		b = PIoT.objects.filter(pk=pk)
		for obj in b:
			sid = obj.sgroup_id
			obj.deploying = False
			obj.save()

	return HttpResponseRedirect('/hardware/')

def software_download(request, pk):
	if request.method == 'GET':
		mysoft = SoftwareGroup.objects.filter(pk=pk)
		print(settings.MEDIA_ROOT)
		for a in mysoft:
			actual_software = re.search(rf'(Hive/software/IoT/)(.*)', str(a.software))
			ipk = a.pk
		a_soft = actual_software.group(2)

		initpath = settings.MEDIA_ROOT + 'software/Staging/' + str(ipk) + '/' + str(a_soft)
		fl_path = initpath
		filename = str(a_soft)
		fl = open(fl_path, 'r')
		mime_type, _ = mimetypes.guess_type(fl_path)
		response = HttpResponse(fl, content_type=mime_type)
		response['Content-Disposition'] = "attachment; filename=%s" % filename
		return response

	#return render(request, 'sdownload.html', context={'mysoft': mysoft})
class SoftwareUpdateView(BSModalUpdateView):
	model = SoftwareGroup
	template_name = 'update_software.html'
	form_class = SoftwareUpdateForm
	success_message = 'Success: Software Group was updated.'
	success_url = reverse_lazy('index')

	def post(self, request, pk):
		if self.request.is_ajax():
			print(request.POST['submit'])
			if 'updateSoftwareGroup' in self.request.POST:
				print('True')
		return HttpResponseRedirect('/software/')



class SoftwareEditorView(TemplateView):
	def get(self, request, pk):
		if request.method == 'GET':

			mysoft = SoftwareGroup.objects.filter(pk=pk)
			for a in mysoft:
				mysoftware = a.software
				b = mysoftware.path
			f =  open(b, 'r')
			lines = f.read()
			#print(lines)
			f.close()
			#print(lines)
			form = SoftwareEditForm()
		return render(request, 'software_editor.html', context={'form': form, 'lines': lines})

	def post(self, request, pk):
		if request.method == 'POST':
			print(request.POST.get('software'))
			string = str(request.POST.get('software')).replace("&nbsp;", " ")
			string2 = str(string).replace("<br />", "\n")
			string3 = str(string2).replace("<pre>", "")
			string4 = str(string3).replace("</pre>", "")
			mysoft = SoftwareGroup.objects.filter(pk=pk)
			for a in mysoft:
				mysoftware = a.software
				b = mysoftware.path
			f =  open(b, 'w')
			f.write(string4)
			f.close()
			url = '/software/' + str(pk) + '/editor/'
		return HttpResponseRedirect(str(url))

