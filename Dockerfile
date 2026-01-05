# Temel imaj olarak Python kullan
FROM python:3.9-slim

# Gerekli sistem araçlarını ve Chrome'u yükle
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean

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
