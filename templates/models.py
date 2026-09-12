from django.db import models

class SiteAyarlari(models.Model):
    """Sitedeki sabit bilgileri (Telefon, Logo, Slogan vb.) buradan yönetirsin."""
    site_adi = models.CharField(max_length=100, default="Arınç Tesisat")
    telefon = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20)
    adres = models.TextField()
    email = models.EmailField()
    hero_baslik = models.CharField(max_length=200, help_text="Ana sayfadaki büyük başlık")
    hero_alt_metin = models.TextField(help_text="Başlığın altındaki açıklama")
    
    class Meta:
        verbose_name = "Site Ayarı"
        verbose_name_plural = "Site Ayarları"

class Hizmet(models.Model):
    """8 hizmet kartını buradan ekleyip çıkarabilirsin."""
    baslik = models.CharField(max_length=100)
    aciklama = models.TextField()
    ikon = models.CharField(max_length=50, help_text="FontAwesome ikon kodu (örn: fa-house-crack)")
    sira = models.IntegerField(default=0, help_text="Sitedeki görünüm sırası")
    aktif_mi = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hizmet"
        verbose_name_plural = "Hizmetler"

class MusteriYorumu(models.Model):
    """Müşteri yorumlarını yönetmek için."""
    isim = models.CharField(max_length=100)
    yorum = models.TextField()
    yildiz = models.IntegerField(default=5)

    class Meta:
        verbose_name = "Müşteri Yorumu"
        verbose_name_plural = "Müşteri Yorumları"