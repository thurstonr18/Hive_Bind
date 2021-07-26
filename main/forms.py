from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import PIoT, SoftwareGroup
from tinymce.widgets import TinyMCE
from django.conf import settings
from bootstrap_modal_forms.forms import BSModalModelForm
from tinymce.widgets import TinyMCE



class PIoTForm(forms.ModelForm):
	class Meta:
		model = PIoT
		fields = '__all__'


class PIoTUpdateForm(BSModalModelForm):
    class Meta:
        model = PIoT
        fields = '__all__'
        labels = {
            'sgroup': 'Software Group'
            }
class SoftwareForm(forms.ModelForm):
    destination = forms.CharField(label='Destination', widget=forms.TextInput(attrs={'onClick': 'clearForm()', 'value': '/home/pi/'}))
    software = forms.FileField(
        label='Select a file',
    )
    class Meta:
        model = SoftwareGroup
        fields = ['name', 'version']

class command_form(forms.Form):
    cmd = forms.CharField(max_length=200)


class SoftwareUpdateForm(BSModalModelForm):
    class Meta:
        model = SoftwareGroup
        fields = ['name', 'version', 'destination', 'software']
        labels = {
            'sgroup': 'Software Group'
            }


class SoftwareEditForm(forms.Form):
    software = forms.CharField(label="", required=False, widget=TinyMCE(attrs={'style': 'height: 650px'}))
    
#class UserLoginForm(AuthenticationForm):
#    def __init__(self, *args, **kwargs):
#        super(UserLoginForm, self).__init__(*args, **kwargs)
#
#    #username = forms.EmailField(widget=forms.TextInput(
#     #   attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'}))
#
#    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'value': 'Username'}))
#    password = forms.CharField(widget=forms.PasswordInput(
#        attrs={
#            'class': 'form-control',
#            'value': 'Password',
#            'placeholder': '',           
#        }
#))
#
