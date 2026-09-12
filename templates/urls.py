from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # JET URL'leri
    path('admin/', admin.site.urls),
    path('', include('senin_uygulaman.urls')), # Ana sayfa bağlantıların
]