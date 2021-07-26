
from django.contrib import admin 
from django.urls import path
from . import views
from . import static
from . import forms
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('dashboard/', login_required(views.IndexView.as_view()), name='index'),
    path('post_device/', views.post_device, name='post_device'),
    path('hardware/', login_required(views.HardwareView.as_view()), name='hardware_view'),
    path('software/', login_required(views.SoftwareView.as_view()), name='software_view'),
    path('hardware/<int:pk>/', login_required(views.PIoTUpdateView.as_view()), name='update_hardware'),
    path('hardware/pi/<int:pk>/', login_required(views.AutoPiUpdateView.as_view()), name='update_pi'),
    path('hardware/pi/status/<int:pk>/', login_required(views.AutoPiStatusView.as_view()), name='update_pi_status'),
    path('hardware/details/<int:pk>/', login_required(views.PotPi.as_view()), name='pi_details'),
    path('hardwares/', views.hardwares, name='hardwares'),
    path('software/<int:pk>/', login_required(views.SoftwareUpdateView.as_view()), name='update_software'),
    path('software/<int:pk>/editor/', login_required(views.SoftwareEditorView.as_view()), name='edit_software'),
    path('software_download/<int:pk>/', views.software_download, name='software_download'),
    path('softwares/', views.softwares, name='softwares'),
    path('vpn_list/', views.vpn_list, name='vpn_list'),
    path('determination/', login_required(views.Determination.as_view()), name='determination'),
    path('hwdetermination/<int:pk>/', login_required(views.hardware_determination), name='hwdetermination'),
    path('determination/<int:pk>/', login_required(views.Removal.as_view()), name='removal'),
    path('hwdetermination/<int:pk>/removal/', login_required(views.hardware_determination_removal), name='hwdeterminationremoval'),
    
    path('ajax_call/', views.call, name='ajax_call')



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
