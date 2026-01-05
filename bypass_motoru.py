import time
import random
import os
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

# SENİN WEBSHARE PROXY LİSTEN (IP:PORT:USER:PASS)
PROXIES = [
    "142.111.48.253:7030:ghpgyqms:dbikygdy4w97",
    "23.95.150.145:6114:ghpgyqms:dbikygdy4w97",
    "198.23.239.134:6540:ghpgyqms:dbikygdy4w97",
    "107.172.163.27:6543:ghpgyqms:dbikygdy4w97",
    "198.105.121.200:6462:ghpgyqms:dbikygdy4w97",
    "64.137.96.74:6641:ghpgyqms:dbikygdy4w97",
    "84.247.60.125:6095:ghpgyqms:dbikygdy4w97",
    "216.10.27.159:6837:ghpgyqms:dbikygdy4w97",
    "23.26.71.145:5628:ghpgyqms:dbikygdy4w97",
    "23.27.208.120:5830:ghpgyqms:dbikygdy4w97"
]

def get_proxy_auth_extension(proxy):
    """
    Şifreli Proxy'leri Selenium'a yedirmek için anlık eklenti oluşturur.
    """
    try:
        ip, port, user, password = proxy.split(":")
    except:
        return None # Format bozuksa

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (ip, port, user, password)

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return plugin_file

def get_driver():
    options = Options()
    options.add_argument("--headless") # Arka planda çalıştır
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Rastgele User-Agent
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    
    # Rastgele Proxy Seç ve Eklentiyi Oluştur
    selected_proxy = random.choice(PROXIES)
    plugin_file = get_proxy_auth_extension(selected_proxy)
    
    if plugin_file:
        options.add_extension(plugin_file)

    # Render'da Chrome yolu bazen sorun olur, otomatik bulsun
    driver = webdriver.Chrome(options=options)
    return driver

def start_bypass_process(url):
    driver = None
    try:
        driver = get_driver()
        driver.set_page_load_timeout(30) # 30 saniye bekleme süresi
        
        # Linke git
        print(f"Bypass deneniyor: {url}")
        driver.get(url)
        time.sleep(3) # Yüklenmesini bekle

        # --- BURASI SİTEYE GÖRE DEĞİŞİR ---
        # Örnek: Başlığı alıp dönelim ki çalıştığını gör.
        title = driver.title
        final_url = driver.current_url
        
        # Geçici Başarı Mesajı
        return {"status": "success", "url": final_url, "title": title}

    except Exception as e:
        print(f"Hata: {e}")
        return {"status": "error", "msg": str(e)}
    finally:
        if driver: driver.quit()
        # Geçici eklenti dosyasını temizle
        if os.path.exists('proxy_auth_plugin.zip'):
            os.remove('proxy_auth_plugin.zip')
