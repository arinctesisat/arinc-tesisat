from django.contrib import admin
from .models import SiteAyarlari, Hizmet, MusteriYorumu

@admin.register(SiteAyarlari)
class SiteAyarlariAdmin(admin.ModelAdmin):
    # Ayarların sadece tek bir satır olmasını sağlar (birden fazla ayar seti olmaz)
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else True

@admin.register(Hizmet)
class HizmetAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'sira', 'aktif_mi')
    list_editable = ('sira', 'aktif_mi')
    search_fields = ('baslik',)

@admin.register(MusteriYorumu)
class MusteriYorumuAdmin(admin.ModelAdmin):
    list_display = ('isim', 'yildiz')