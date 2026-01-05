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

# WEBSHARE PROXY LİSTEN
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
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # --- ANTI-DETECT AYARLARI (HAYALET MOD) ---
    # Bu ayarlar bot olduğunu gizler
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    
    if PROXIES:
        selected_proxy = random.choice(PROXIES)
        plugin_file = get_proxy_auth_extension(selected_proxy)
        if plugin_file:
            options.add_extension(plugin_file)

    driver = webdriver.Chrome(options=options)
    
    # Selenium izlerini sil
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

# ==================== GÖREV FONKSİYONU ====================
def solve_verification_steps(driver):
    print("🕵️ GÖREV MODU BAŞLATILIYOR...")
    main_window = driver.current_window_handle
    
    try:
        # 1. BAŞLAT BUTONU
        # Farklı varyasyonları dene
        xpaths = [
            "//button[contains(text(), 'Doğrulamayı Başlat')]",
            "//a[contains(text(), 'Doğrulamayı Başlat')]",
            "//div[contains(@class, 'g-recaptcha')]", # Bazen direkt captcha vardır
            "//iframe[contains(@src, 'recaptcha')]"
        ]
        
        found = False
        for xpath in xpaths:
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", btn)
                print("✅ Başlat/Captcha tıklandı.")
                found = True
                break
            except: continue
            
        if not found: print("⚠️ Başlat butonu bulunamadı.")

        time.sleep(5)

        # 2. GOOGLE ARAMA (Sekme değiştiyse)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            print("🔀 Yeni sekmeye geçildi.")
            
            # Google sonucuna tıkla
            try:
                res = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g a")))
                driver.execute_script("arguments[0].click();", res)
                print("✅ Siteye girildi.")
            except: 
                print("⚠️ Google sonucu bulunamadı, belki direkt sitedeyiz.")

        # 3. GEZİNME VE REKLAM
        print("⏳ 10 Saniye geziniliyor...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(5)
        
        # Reklam Tıkla
        try:
            ads = driver.find_elements(By.CSS_SELECTOR, "iframe, ins.adsbygoogle, a[href*='googleadservices']")
            if ads:
                print(f"🖱️ {len(ads)} adet reklam/iframe bulundu. İlkine tıklanıyor.")
                driver.execute_script("arguments[0].click();", ads[0])
                time.sleep(5)
        except: pass

        # 4. GERİ DÖN VE KONTROL ET
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(main_window)
        
        print("🔙 Ana sayfaya dönüldü.")
        time.sleep(2)
        
        try:
            chk = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kontrol Et')] | //a[contains(text(), 'Kontrol Et')]")))
            driver.execute_script("arguments[0].click();", chk)
            print("✅ 'Kontrol Et' tıklandı.")
            time.sleep(5)
        except: print("⚠️ Kontrol Et butonu yok.")

    except Exception as e:
        print(f"Hata: {e}")

# ==================== ANA MOTOR ====================
def start_bypass_process(url):
    driver = None
    try:
        driver = get_driver()
        driver.set_page_load_timeout(60)
        
        print(f"🌍 Link: {url}")
        driver.get(url)
        initial_url = driver.current_url
        time.sleep(5)

        # GÖREV VAR MI?
        src = driver.page_source
        if "Doğrulamayı Başlat" in src or "recaptcha" in src:
            solve_verification_steps(driver)
        else:
            # Genel Butonlar
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Devam')]|//button[contains(text(),'Devam')]")))
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(5)
            except: pass

        final_url = driver.current_url
        
        # HATA DURUMUNDA FOTOĞRAF ÇEK
        if final_url == initial_url or final_url == url:
             driver.save_screenshot("debug_screenshot.png") # <--- FOTOĞRAF ÇEKİYORUZ
             return {"status": "error", "msg": "Sayfa değişmedi. Hata fotosuna bak: /debug"}

        return {"status": "success", "url": final_url}

    except Exception as e:
        if driver: driver.save_screenshot("debug_screenshot.png")
        return {"status": "error", "msg": str(e)}
    finally:
        if driver: 
            try: driver.quit() 
            except: pass
        if os.path.exists('proxy_auth_plugin.zip'):
            os.remove('proxy_auth_plugin.zip')
