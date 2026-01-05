import time
import random
import os
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    """Proxy kimlik doğrulaması için eklenti oluşturur"""
    try:
        ip, port, user, password = proxy.split(":")
    except: return None 

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {scheme: "http", host: "%s", port: parseInt(%s)},
              bypassList: ["localhost"]
            }
          };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {authCredentials: {username: "%s", password: "%s"}};
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn, {urls: ["<all_urls>"]}, ['blocking']
    );
    """ % (ip, port, user, password)

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_file

def get_driver():
    options = Options()
    # Render'da mecburi headless (ekransız) mod
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    
    if PROXIES:
        selected_proxy = random.choice(PROXIES)
        plugin_file = get_proxy_auth_extension(selected_proxy)
        if plugin_file:
            options.add_extension(plugin_file)

    driver = webdriver.Chrome(options=options)
    return driver

# ==================== ÖZEL GÖREV FONKSİYONU ====================
def solve_verification_steps(driver):
    """
    1- Doğrulamayı Başlat -> 2- Google Araması -> 3- 15sn Bekle -> 4- Reklam Tıkla -> 5- Kontrol Et
    """
    print("🕵️ GÖREV MODU BAŞLATILIYOR...")
    main_window = driver.current_window_handle
    
    try:
        # ADIM 1: 'Doğrulamayı Başlat' Butonunu bul
        # (Sitede bu yazıyı içeren butona tıklar)
        try:
            start_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Doğrulamayı Başlat')] | //a[contains(text(), 'Doğrulamayı Başlat')]"))
            )
            driver.execute_script("arguments[0].click();", start_btn)
            print("✅ 'Doğrulamayı Başlat' tıklandı.")
        except:
            print("⚠️ Başlat butonu bulunamadı, devam ediliyor...")

        # ADIM 2: Yeni Sekme Açıldı mı? (Google Araması)
        time.sleep(5)
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1]) # Yeni sekmeye geç
            print("🔀 Google sayfasına geçildi.")
            
            # Google'daki ilk sonuca tıkla (Reklam olmayan)
            try:
                first_res = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g a h3")))
                parent = first_res.find_element(By.XPATH, "./..")
                driver.execute_script("arguments[0].click();", parent)
                print("✅ Siteye girildi.")
            except:
                print("⚠️ Google sonucu tıklanamadı.")
        
        # ADIM 3: Sitede 15 Saniye Gezin
        print("⏳ 15 Saniye bekleniyor...")
        for i in range(15):
            driver.execute_script(f"window.scrollTo(0, {i * 50});") # Sayfayı kaydır
            time.sleep(1)

        # ADIM 4: Reklam Bul ve Tıkla
        print("🖱️ Reklam aranıyor...")
        ad_clicked = False
        try:
            # Yaygın reklam kodlarını arar
            ads = driver.find_elements(By.CSS_SELECTOR, "iframe[id*='google_ads'], ins.adsbygoogle")
            if ads:
                driver.execute_script("arguments[0].click();", ads[0])
                print("✅ Reklama Tıklandı!")
                ad_clicked = True
                time.sleep(5) # Reklamda 5 sn bekle
            else:
                print("⚠️ Reklam bulunamadı.")
        except: pass

        # ADIM 5: Geri Dön ve Kontrol Et
        if len(driver.window_handles) > 1:
            driver.close() # Reklam/Site sekmesini kapat
            driver.switch_to.window(main_window) # Ana sayfaya dön
        
        print("🔙 Ana sayfaya dönüldü, 'Kontrol Et' aranıyor...")
        time.sleep(2)
        
        try:
            check_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontrol Et')] | //a[contains(text(), 'Kontrol Et')]"))
            )
            driver.execute_script("arguments[0].click();", check_btn)
            print("✅ 'Kontrol Et' butonuna basıldı!")
            time.sleep(5) # Yönlendirme beklemesi
        except:
            print("⚠️ Kontrol Et butonu bulunamadı.")

    except Exception as e:
        print(f"🔥 Görev Hatası: {e}")
        try: driver.switch_to.window(main_window)
        except: pass

# ==================== ANA ÇALIŞTIRICI ====================
def start_bypass_process(url):
    driver = None
    try:
        driver = get_driver()
        driver.set_page_load_timeout(60) # 60 saniye mühlet
        
        print(f"🌍 Linke gidiliyor: {url}")
        driver.get(url)
        initial_url = driver.current_url
        time.sleep(3)

        # Sayfa kaynağını alıp kontrol et: Görev var mı?
        page_source = driver.page_source
        if "Doğrulamayı Başlat" in page_source:
            solve_verification_steps(driver)
        else:
            # Görev yoksa normal butonları dene (Devam Et vb.)
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Devam Et')] | //button[contains(text(), 'Devam Et')]")))
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(5)
            except: pass

        final_url = driver.current_url
        print(f"🏁 Sonuç: {final_url}")
        
        if final_url == initial_url or final_url == url:
             return {"status": "error", "msg": "Bypass başarısız, sayfa değişmedi."}

        return {"status": "success", "url": final_url}

    except Exception as e:
        return {"status": "error", "msg": str(e)}
    finally:
        if driver: 
            try: driver.quit() 
            except: pass
        if os.path.exists('proxy_auth_plugin.zip'):
            os.remove('proxy_auth_plugin.zip')
