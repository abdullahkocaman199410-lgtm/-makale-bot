import requests
import json
import time
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WP_URL = os.environ.get("WP_URL")
WP_USER = os.environ.get("WP_USER")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")

GOREVLER = [
    {"konu": "OEM çanta üretimi", "dil": "Türkçe"},
    {"konu": "OEM bag manufacturing", "dil": "İngilizce"},
    {"konu": "OEM Taschenherstellung", "dil": "Almanca"},
    {"konu": "fabrication de sacs OEM", "dil": "Fransızca"},
    {"konu": "produzione borse OEM", "dil": "İtalyanca"},
    {"konu": "OEM tas productie", "dil": "Felemenkçe"},
    {"konu": "تصنيع الحقائب OEM", "dil": "Arapça"},
    {"konu": "toptan çanta üretimi", "dil": "Türkçe"},
    {"konu": "wholesale bag production", "dil": "İngilizce"},
    {"konu": "özel logo çanta", "dil": "Türkçe"},
    {"konu": "custom logo bags", "dil": "İngilizce"},
    {"konu": "Taschen mit eigenem Logo", "dil": "Almanca"},
    {"konu": "sacs personnalisés logo", "dil": "Fransızca"},
    {"konu": "borse logo personalizzato", "dil": "İtalyanca"},
    {"konu": "tassen eigen logo", "dil": "Felemenkçe"},
    {"konu": "حقائب بشعار مخصص", "dil": "Arapça"},
    {"konu": "wholesale bag manufacturer Europe", "dil": "İngilizce"},
    {"konu": "wholesale bag manufacture", "dil": "İngilizce"},
    {"konu": "Großhandel Taschenherstellung", "dil": "Almanca"},
    {"konu": "fabrication sacs en gros", "dil": "Fransızca"},
    {"konu": "produzione borse all'ingrosso", "dil": "İtalyanca"},
    {"konu": "groothandel tassenproductie", "dil": "Felemenkçe"},
    {"konu": "تصنيع الحقائب بالجملة", "dil": "Arapça"},
    {"konu": "toptan çanta imalatı", "dil": "Türkçe"},
]

def makale_yaz(konu, dil):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""Write a comprehensive, SEO-optimized blog article about '{konu}' in {dil} language.

    Requirements:
    - Start with an SEO-optimized title (H1) that includes the main keyword naturally. Do NOT use brackets or language labels in the title.
    - Write a compelling introduction paragraph
    - Include at least 5 subheadings (H2)
    - Detailed content under each subheading
    - Include a FAQ section with at least 3 questions
    - Write a conclusion paragraph
    - Minimum 2500 words
    - Use HTML format: <h1> for title, <h2> for subheadings, <p> for paragraphs
    - Write ONLY in {dil} language
    - The title must be catchy and include the keyword naturally"""

    payload = {{"contents": [{{"parts": [{{"text": prompt}}]}}]}}
    response = requests.post(url, json=payload)
    data = response.json()
    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        # Extract title from H1 tag
        import re
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        else:
            title = konu
        return title, content
    except:
        print(f"Hata: {data}")
        return None, None

def wordpress_yayinla(baslik, icerik, meta_aciklama=""):
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    auth = (WP_USER, WP_APP_PASSWORD)
    payload = {{
        "title": baslik,
        "content": icerik,
        "status": "publish"
    }}
    response = requests.post(url, json=payload, auth=auth)
    if response.status_code == 201:
        post = response.json()
        print(f"✅ Yayınlandı: {post['link']}")
        return True
    else:
        print(f"❌ Hata: {response.status_code} - {response.text}")
        return False

def main():
    print("🚀 Çok dilli makale botu başlıyor...\n")
    for i, gorev in enumerate(GOREVLER, 1):
        print(f"[{i}/{len(GOREVLER)}] 📝 {gorev['dil']}: {gorev['konu']}")
        baslik, icerik = makale_yaz(gorev["konu"], gorev["dil"])
        if icerik:
            wordpress_yayinla(baslik, icerik)
        print(f"⏳ 5 saniye bekleniyor...\n")
        time.sleep(5)
    print("✅ Tüm makaleler tamamlandı!")

if __name__ == "__main__":
    main()
