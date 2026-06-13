import requests
import os
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
import json
import time
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WP_URL = os.environ.get("WP_URL")
WP_USER = os.environ.get("WP_USER")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD")

GOREVLER = [
    {"konu": "private label bag manufacturer Turkey", "dil": "İngilizce"},
    {"konu": "OEM bag factory Turkey", "dil": "İngilizce"},
    {"konu": "custom bag manufacturer Turkey", "dil": "İngilizce"},
    {"konu": "promotional bag manufacturer", "dil": "İngilizce"},
    {"konu": "branded bag manufacturer Europe", "dil": "İngilizce"},
    {"konu": "diaper bag manufacturer", "dil": "İngilizce"},
    {"konu": "OEM diaper bag manufacturer", "dil": "İngilizce"},
    {"konu": "custom diaper bag manufacturer Turkey", "dil": "İngilizce"},
    {"konu": "wholesale diaper bag production", "dil": "İngilizce"},
    {"konu": "private label diaper bag manufacturer", "dil": "İngilizce"},
    {"konu": "diaper bag üretimi", "dil": "Türkçe"},
    {"konu": "bebek bezi çantası üretimi", "dil": "Türkçe"},
    {"konu": "özel diaper bag imalatı", "dil": "Türkçe"},
    {"konu": "promosyon çanta üretimi", "dil": "Türkçe"},
    {"konu": "özel tasarım çanta üretim", "dil": "Türkçe"},
    {"konu": "Wickeltaschen Hersteller", "dil": "Almanca"},
    {"konu": "OEM Wickeltaschen Produktion", "dil": "Almanca"},
    {"konu": "Werbetaschen Hersteller", "dil": "Almanca"},
    {"konu": "fabricant sac a langer", "dil": "Fransızca"},
    {"konu": "sac a langer OEM fabricant", "dil": "Fransızca"},
    {"konu": "fabricant sac publicitaire", "dil": "Fransızca"},
    {"konu": "produttore borsa fasciatoio", "dil": "İtalyanca"},
    {"konu": "borsa fasciatoio OEM produttore", "dil": "İtalyanca"},
    {"konu": "produttore borse promozionali", "dil": "İtalyanca"},
    {"konu": "luiertas fabrikant", "dil": "Felemenkçe"},
    {"konu": "OEM luiertas productie", "dil": "Felemenkçe"},
    {"konu": "promotie tassen fabrikant", "dil": "Felemenkçe"},
    {"konu": "مصنع حقيبة الحفاضات", "dil": "Arapça"},
    {"konu": "حقيبة حفاضات OEM مخصصة", "dil": "Arapça"},
    {"konu": "مصنع حقائب بالجملة تركيا", "dil": "Arapça"},
]

def yukle_gorsel(gorsel_url):
    try:
        img_data = requests.get(gorsel_url).content
        media_url = f"{WP_URL}/wp-json/wp/v2/media"
        auth = (WP_USER, WP_APP_PASSWORD)
        headers = {"Content-Disposition": "attachment; filename=gorsel.jpg", "Content-Type": "image/jpeg"}
        response = requests.post(media_url, data=img_data, headers=headers, auth=auth)
        if response.status_code == 201:
            return response.json()["id"]
    except:
        pass
    return None

def gorsel_getir(konu):
    try:
        url = f"https://api.unsplash.com/search/photos?query={konu}&per_page=1&client_id={UNSPLASH_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                return data["results"][0]["urls"]["regular"]
    except:
        pass
    return None

def son_makaleleri_getir():
    try:
        url = f"{WP_URL}/wp-json/wp/v2/posts?per_page=5&status=publish&orderby=date"
        response = requests.get(url)
        if response.status_code == 200:
            posts = response.json()
            return [(p['title']['rendered'], p['link']) for p in posts]
    except:
        pass
    return []

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

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
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

def wordpress_yayinla(baslik, icerik, meta_aciklama="", gorsel_url=None):
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    auth = (WP_USER, WP_APP_PASSWORD)
    payload = {
        "title": baslik,
        "content": icerik,
        "status": "publish"
    }
    if gorsel_url:
        payload["featured_media"] = yukle_gorsel(gorsel_url)
    response = requests.post(url, json=payload, auth=auth)
    if response.status_code == 201:
        post = response.json()
        print(f"✅ Yayınlandı: {post['link']}")
        return True
    else:
        print(f"❌ Hata: {response.status_code} - {response.text}")
        return False

def main():
    import random
    adet = random.randint(11, 15)
    secilen = random.sample(GOREVLER, adet)
    print(f"🚀 Bugün {adet} makale yazılacak...\n")
    for i, gorev in enumerate(secilen, 1):
        print(f"[{i}/{len(GOREVLER)}] 📝 {gorev['dil']}: {gorev['konu']}")
        baslik, icerik = makale_yaz(gorev["konu"], gorev["dil"])
        if icerik:
            gorsel_url = gorsel_getir(gorev["konu"])
            wordpress_yayinla(baslik, icerik, gorsel_url=gorsel_url)
        print(f"⏳ 5 saniye bekleniyor...\n")
        time.sleep(5)
    print("✅ Tüm makaleler tamamlandı!")

if __name__ == "__main__":
    main()
