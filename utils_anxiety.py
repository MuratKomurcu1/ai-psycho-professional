import os
import json
import time
import threading
from datetime import datetime
import numpy as np
import io
import wave
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# OpenAI v1.0+ import
from openai import OpenAI
import streamlit as st

# Konfigürasyon
class Config:
    def __init__(self):
        self.OPENAI_API_KEY = (
            os.getenv("OPENAI_API_KEY") or 
            st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, 'secrets') else None
        )

config = Config()

# Global değişkenler
openai_client = None

def openai_baslat():
    """OpenAI client'ı başlat"""
    global openai_client
    if config.OPENAI_API_KEY:
        try:
            openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            print("✅ OpenAI client başlatıldı")
            return True
        except Exception as e:
            print(f"❌ OpenAI client hatası: {e}")
            return False
    return False

def kullanici_veri_yukle(kullanici_adi):
    """Kullanıcı verisini JSON'dan yükle"""
    try:
        dosya_yolu = f"kullanici_verileri/{kullanici_adi}.json"
        if os.path.exists(dosya_yolu):
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Kullanıcı veri yükleme hatası: {e}")
        return None

def kullanici_veri_kaydet(kullanici_adi, veri):
    """Kullanıcı verisini JSON'a kaydet"""
    try:
        dosya_yolu = f"kullanici_verileri/{kullanici_adi}.json"
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Kullanıcı veri kaydetme hatası: {e}")
        return False

def sesi_metne_cevir_openai(ses_verisi):
    """OpenAI Whisper ile ses-metin çevirisi"""
    try:
        if not openai_client:
            print("❌ OpenAI client yok")
            return "API istemcisi yapılandırılmamış"
        
        gecici_dosya = "temp_audio.wav"
        with open(gecici_dosya, 'wb') as f:
            f.write(ses_verisi)
        
        print(f"📁 Whisper için dosya hazır: {len(ses_verisi)} byte")
        
        with open(gecici_dosya, 'rb') as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="tr"
            )
        
        try:
            os.remove(gecici_dosya)
        except:
            pass
            
        result = transcript.text.strip()
        print(f"🎯 Whisper sonucu: '{result}'")
        return result
        
    except Exception as e:
        print(f"❌ OpenAI transkripsiyon hatası: {e}")
        return None

def metinden_sese_openai(metin):
    """OpenAI TTS ile metin-ses çevirisi"""
    try:
        if not openai_client:
            print("❌ OpenAI client yok - TTS yapılamaz")
            return None
            
        print(f"🎵 TTS için metin: '{metin[:50]}...'")
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=metin,
            speed=0.85
        )
        
        print("✅ TTS başarılı")
        return response.content
        
    except Exception as e:
        print(f"❌ OpenAI TTS hatası: {e}")
        return None

def ses_baytlarini_cal(ses_baytlari):
    """Ses dosyasını çal"""
    try:
        gecici_dosya = "gecici_ai_psycho_ses.mp3"
        with open(gecici_dosya, "wb") as f:
            f.write(ses_baytlari)
        
        print("🔊 Ses dosyası hazırlandı, çalınıyor...")
        
        import pygame
        pygame.mixer.quit()
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        pygame.mixer.music.load(gecici_dosya)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        pygame.mixer.quit()
        
        try:
            os.remove(gecici_dosya)
        except:
            pass
        
        print("🔊 Ses başarıyla çalındı")
        return True
            
    except Exception as e:
        print(f"❌ Ses çalma hatası: {e}")
        return False

def metinden_stres_analizi(metin):
    """Metinden stres ve ruh hali analizi"""
    try:
        if not openai_client:
            return 5, "normal"
            
        stres_promptu = f"""Bu metindeki stres/anksiyete seviyesini analiz et. 0-10 arası puanla:
0 = Çok sakin, huzurlu
1-3 = Hafif endişeli/kaygılı  
4-6 = Orta düzey anksiyete/stres
7-9 = Yüksek anksiyete/stres
10 = Şiddetli panik/kriz

Metin: "{metin}"

Sadece bir sayı (0-10) ve bir kelime ruh hali (sakin/endişeli/anksiyeteli/stresli/panik) ile cevap ver.
Format: "7 anksiyeteli"
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": stres_promptu}],
            max_tokens=10,
            temperature=0.1
        )
        
        sonuc = response.choices[0].message.content.strip().split()
        stres_seviyesi = int(sonuc[0])
        ruh_hali = sonuc[1] if len(sonuc) > 1 else "normal"
        
        return stres_seviyesi, ruh_hali
        
    except Exception as e:
        print(f"❌ Stres analizi hatası: {e}")
        return 5, "normal"

def ai_psikolog_cevap_uret(kullanici_metni, problem_bilgisi, konusma_gecmisi, konusma_sirasi):
    """AI psikolog cevabı üret"""
    try:
        if not openai_client:
            return "Size destek olmak için buradayım. Nasıl yardımcı olabilirim?"
        
        # Konuşma geçmişi
        baglam = ""
        if konusma_gecmisi:
            for konusma in konusma_gecmisi[-3:]:
                baglam += f"Danışan: {konusma['kullanici']}\nPsikolog: {konusma['ai']}\n"
        
        # Seans aşamasına göre yaklaşım
        if konusma_sirasi == 0:
            asama_talimat = """İLK KONUŞMA - Karşılama ve bağ kurma:
- Hastanın problemini anlayın
- Empati kurun, güven verin
- Açık uçlu sorular sorun
- Yargılamadan dinleyin"""
        elif konusma_sirasi <= 2:
            asama_talimat = """ORTA AŞAMA - Keşif ve değerlendirme:
- Daha derin sorular sorun
- Tetikleyici faktörleri araştırın
- Geçmiş deneyimleri inceleyin
- Başa çıkma mekanizmalarını keşfedin"""
        else:
            asama_talimat = """SON AŞAMA - Müdahale ve öneriler:
- Pratik çözümler sunun
- Başa çıkma stratejileri öğretin
- Ev ödevleri verin
- Umudu artırın"""
        
        # Problem aciliyet seviyesi
        aciliyet_yaklaşımı = ""
        if problem_bilgisi["aciliyet"] == "Acil yardım gerekli":
            aciliyet_yaklaşımı = "ÖNEMLİ: Hasta acil durum bildirdi. Derhal sakinleştirici teknikler uygulayın."
        elif problem_bilgisi["aciliyet"] == "Ciddi sorun":
            aciliyet_yaklaşımı = "DİKKAT: Ciddi problem var. Profesyonel yaklaşımla destekleyin."
        
        prompt = f"""Sen deneyimli bir klinik psikolog olarak 5 dakikalık kısa seans yapıyorsun.

{asama_talimat}

{aciliyet_yaklaşımı}

BAĞLAM:
Problem: {problem_bilgisi['metin']}
Terapi geçmişi: {problem_bilgisi['terapi_gecmisi']}
Aciliyet: {problem_bilgisi['aciliyet']}

Önceki konuşmalar:
{baglam}

Hasta şimdi şunu söyledi: "{kullanici_metni}"

KURALLAR:
- Türkçe konuş
- 40-60 kelime arası cevap ver
- Klinik psikolog gibi davran
- Empati kur ama profesyonel kal
- Somut öneriler ver
- Hastanın duygularını doğrula

Profesyonel psikolog cevabı ver:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ AI psikolog cevap hatası: {e}")
        return "Anlıyorum... Bu durum sizi nasıl etkiliyor? Biraz daha açabilir misiniz?"

def seans_analizi_yap(problem_bilgisi, konusma_gecmisi):
    """Seans sonunda kapsamlı analiz yap"""
    try:
        if not openai_client:
            return {
                "degerlendirme": "Analiz yapılamadı",
                "oneriler": ["Teknik sorun nedeniyle analiz yapılamadı"],
                "stres_seviyesi": 5,
                "ruh_hali": "belirsiz",
                "aciliyet": "orta"
            }
        
        # Tüm konuşmaları birleştir
        tum_konusmalar = ""
        for konusma in konusma_gecmisi:
            tum_konusmalar += f"Danışan: {konusma['kullanici']}\nPsikolog: {konusma['ai']}\n\n"
        
        analiz_prompt = f"""Sen deneyimli bir klinik psikolog olarak 5 dakikalık bu seansı analiz et.

BAŞLANGIÇ PROBLEMİ:
{problem_bilgisi['metin']}
Aciliyet: {problem_bilgisi['aciliyet']}
Terapi geçmişi: {problem_bilgisi['terapi_gecmisi']}

SEANS TRANSKRİPTİ:
{tum_konusmalar}

Lütfen şu formatta bir analiz yap:

DEĞERLENDIRME: (100-150 kelime profesyonel değerlendirme)
STRES_SEVİYESİ: (0-10 arası sayı)
RUH_HALİ: (sakin/endişeli/anksiyeteli/stresli/depresif/panik kelimelerinden biri)
ACİLİYET: (dusuk/orta/yuksek)
ÖNERİLER: (3-5 madde halinde pratik öneriler)
TEŞHİS_ÖNERİLERİ: (eğer varsa dikkat edilmesi gerekenler)

Analiz yap:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analiz_prompt}],
            max_tokens=400,
            temperature=0.3
        )
        
        analiz_metni = response.choices[0].message.content.strip()
        
        # Analizi parse et
        analiz_sonucu = {
            "degerlendirme": "",
            "oneriler": [],
            "stres_seviyesi": 5,
            "ruh_hali": "normal",
            "aciliyet": "orta",
            "teşhis_onerileri": ""
        }
        
        # Basit parsing
        for satir in analiz_metni.split('\n'):
            if 'DEĞERLENDIRME:' in satir:
                analiz_sonucu["degerlendirme"] = satir.replace('DEĞERLENDIRME:', '').strip()
            elif 'STRES_SEVİYESİ:' in satir:
                try:
                    analiz_sonucu["stres_seviyesi"] = int(satir.replace('STRES_SEVİYESİ:', '').strip())
                except:
                    pass
            elif 'RUH_HALİ:' in satir:
                analiz_sonucu["ruh_hali"] = satir.replace('RUH_HALİ:', '').strip().lower()
            elif 'ACİLİYET:' in satir:
                analiz_sonucu["aciliyet"] = satir.replace('ACİLİYET:', '').strip().lower()
            elif 'ÖNERİLER:' in satir:
                continue
            elif satir.strip().startswith('-') or satir.strip().startswith('•'):
                analiz_sonucu["oneriler"].append(satir.strip()[1:].strip())
            elif 'TEŞHİS_ÖNERİLERİ:' in satir:
                analiz_sonucu["teşhis_onerileri"] = satir.replace('TEŞHİS_ÖNERİLERİ:', '').strip()
        
        # Eğer parsing başarısızsa, tüm metni değerlendirme olarak al
        if not analiz_sonucu["degerlendirme"]:
            analiz_sonucu["degerlendirme"] = analiz_metni
        
        # Varsayılan öneriler
        if not analiz_sonucu["oneriler"]:
            analiz_sonucu["oneriler"] = [
                "Günlük nefes egzersizleri yapın",
                "Düzenli uyku düzenine dikkat edin",
                "Stresi tetikleyen faktörleri belirleyin",
                "Sosyal destek alın",
                "Gerekirse profesyonel yardım arayın"
            ]
        
        return analiz_sonucu
        
    except Exception as e:
        print(f"❌ Seans analizi hatası: {e}")
        return {
            "degerlendirme": "Bu seansda belirlediğimiz temel problemleri ele almaya başladık. Devam etmeniz önerilir.",
            "oneriler": [
                "Günlük stresi azaltma tekniklerini uygulayın",
                "Profesyonel destek almayı düşünün",
                "Kendinize zaman ayırın"
            ],
            "stres_seviyesi": 5,
            "ruh_hali": "normal",
            "aciliyet": "orta"
        }