
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('', RedirectView.as_view(url='accounts/login/', permanent=False), name='home'),
    path('', include('main.urls')),

]
