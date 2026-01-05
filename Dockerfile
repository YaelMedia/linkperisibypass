# Temel imaj olarak Python kullan
FROM python:3.9-slim

# Gerekli sistem araçlarını yükle (apt-key yerine gpg kullanacağız)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    ca-certificates \
    curl \
    --no-install-recommends

# Google Chrome Kurulumu (YENİ GÜVENLİ YÖNTEM)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Dosyaları kopyala
COPY . .

# Python kütüphanelerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Portu aç
EXPOSE 10000

# Uygulamayı başlat
CMD ["python", "app.py"]
