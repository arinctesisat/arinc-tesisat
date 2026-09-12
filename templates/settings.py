INSTALLED_APPS = [
    'jet',  # En üstte olmalı!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Kendi uygulamanın adı (Örn: 'iletisim' veya 'core')
]

# Ayrıca şu ayarı en alta ekle (Panelin Türkçe olması için)
LANGUAGE_CODE = 'tr'