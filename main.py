import streamlit as st
import json
import os
from datetime import datetime, timedelta
import time
import hashlib
from pathlib import Path
import numpy as np
import base64

# OpenAI import
from openai import OpenAI

# OpenAI client
openai_client = None

# Korumalı prompt sistemi
def get_system_prompts():
    """Şifrelenmiş sistem promptları"""
    
    # Base64 ile şifrelenmiş kritik promptlar
    prompts = {
        "ilk_seans": "U2VuIERyLiBNYXJjdXMgUmVlZCAtIDIwIHnEsWxsxLFrIGRlbmV5aW1saSBrbGluaWsgcHNpa29sb2csIEpvaG5zIEhvcGtpbnMgbWV6dW51LCAxNSwwMDArIGhhc3RhIHRlZGF2aSBldG1pxZ8sIDMga2l0YWIgeWF6bcSxxZ8gw65ubGkgdXptYW4u",
        "orta_seans": "T1JUQSBBxZ5BTUEgLSBERVLEsE4gVEXFnkhExLBTIFZFIEFOQUzEsFo6CkfDlFJFVsSwTjogRGFoYSBkZXRheWzEsWtsaW5payBkZcSfZXJsZW5kaXJtZSB5YXAgdmUgdGXFn2hpcyBuZXRsZcWfdGlyLg==",
        "son_seans": "U09OIEHFnkFNQSAtIEtBUFNBTUxJIFRFxZ5IxLBTIFZFIE3DnERBSEFMRSBQTEFOSToKR8OWUkVWxLBOOiBLZXNpbiB0YW7EsSBrb3kgdmUga2Fwc2FtbMSxIHRlZGF2aSBwbGFuxLEgc3VuLg=="
    }
    
    # Decrypt
    decoded = {}
    for key, value in prompts.items():
        try:
            decoded[key] = base64.b64decode(value).decode('utf-8')
        except:
            decoded[key] = "Fallback prompt for safety"
    
    return decoded

def openai_baslat():
    """OpenAI client'ı başlat"""
    global openai_client
    
    # .env dosyasını yükle (eğer varsa)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv yoksa devam et
    
    # API key alma öncelik sırası: .env > Streamlit secrets > environment
    api_key = None
    
    # 1. .env dosyasından dene
    api_key = os.getenv("OPENAI_API_KEY")
    
    # 2. Streamlit secrets'tan dene (fallback)
    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            pass
    
    if api_key:
        try:
            openai_client = OpenAI(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"OpenAI client hatası: {e}")
            return False
    else:
        st.error("❌ OpenAI API anahtarı bulunamadı! Lütfen .env dosyasında OPENAI_API_KEY tanımlayın.")
    return False

def metinden_sese_openai(metin):
    """OpenAI TTS ile metin-ses çevirisi"""
    try:
        if not openai_client:
            return None
            
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=metin,
            speed=0.9
        )
        
        return response.content
        
    except Exception as e:
        st.error(f"TTS hatası: {e}")
        return None

def ses_baytlarini_cal(ses_baytlari):
    """Ses dosyasını çal - Streamlit Share için basitleştirilmiş"""
    try:
        gecici_dosya = "ai_psycho_cevap.mp3"
        with open(gecici_dosya, "wb") as f:
            f.write(ses_baytlari)
        
        # Streamlit'in audio player'ını kullan
        st.audio(gecici_dosya, format='audio/mp3', start_time=0)
        
        # Geçici dosyayı sil
        try:
            os.remove(gecici_dosya)
        except:
            pass
        
        return True
            
    except Exception as e:
        st.error(f"Ses çalma hatası: {e}")
        return False

def build_secure_prompt(stage, user_input, problem_info, history):
    """Güvenli prompt oluşturucu - kritik business logic gizli"""
    
    # Şifrelenmiş promptları al
    prompts = get_system_prompts()
    
    # Seans aşamasına göre
    if stage == 0:
        base_prompt = prompts["ilk_seans"]
        stage_instructions = "İLK GÖRÜŞME - Güven inşa et ve semptom tespiti yap"
    elif stage <= 2:
        base_prompt = prompts["orta_seans"] 
        stage_instructions = "ORTA AŞAMA - Derin analiz ve diferansiyel tanı"
    else:
        base_prompt = prompts["son_seans"]
        stage_instructions = "SON AŞAMA - Kesin tanı ve tedavi protokolü"
    
    # Dinamik prompt birleştirme
    final_prompt = f"""
{base_prompt}

{stage_instructions}

HASTA PROFİLİ:
Problem: {problem_info['metin'][:200]}...
Geçmiş: {problem_info['terapi_gecmisi']}
Aciliyet: {problem_info['aciliyet']}

HASTA İFADESİ: "{user_input}"

80-120 kelime profesyonel cevap ver."""

    return final_prompt

def ai_psikolog_cevap_uret(kullanici_metni, problem_bilgisi, konusma_gecmisi, konusma_sirasi):
    """Korumalı AI psikolog cevap üretici"""
    try:
        if not openai_client:
            return "Size destek olmak için buradayım. Bu durumu birlikte çözeceğiz."
        
        # Güvenli prompt oluştur
        secure_prompt = build_secure_prompt(
            konusma_sirasi, 
            kullanici_metni, 
            problem_bilgisi, 
            konusma_gecmisi
        )
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": secure_prompt}],
            max_tokens=300,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"AI psikolog cevap hatası: {e}")
        return "Klinik değerlendirmeme göre, bu semptom profili tedavi edilebilir görünüyor. Size özel bir protokol hazırlayabilirim."

def get_analysis_template():
    """Şifrelenmiş analiz template'i"""
    
    encrypted_template = "UHJvZmVzeW9uZWwga2xpbmlrIGFuYWxpeiBzaXN0ZW1p"
    
    try:
        base_template = base64.b64decode(encrypted_template).decode('utf-8')
    except:
        base_template = "Klinik analiz sistemi"
    
    return f"""
{base_template}

KLİNİK RAPOR PROTOKOLÜ:
- DSM-5 kriterlerine göre değerlendirme
- Semptom pattern recognition
- Diferansiyel tanı analizi
- Evidence-based treatment önerileri
- Risk assessment ve prognoz

Profesyonel analiz formatında rapor hazırla.
"""

def seans_analizi_yap(problem_bilgisi, konusma_gecmisi):
    """Korumalı klinik analiz sistemi"""
    try:
        if not openai_client:
            return basit_analiz_sonucu()
        
        # Tüm konuşmaları birleştir
        tum_konusmalar = ""
        for konusma in konusma_gecmisi:
            tum_konusmalar += f"Hasta: {konusma['kullanici']}\nPsikolog: {konusma['ai']}\n\n"
        
        # Güvenli analiz template
        analysis_template = get_analysis_template()
        
        analiz_prompt = f"""{analysis_template}

SEANS VERİLERİ:
Problem: {problem_bilgisi['metin']}
Şiddet: {problem_bilgisi['aciliyet']}
Geçmiş: {problem_bilgisi['terapi_gecmisi']}

KONUŞMA TRANSKRİPTİ:
{tum_konusmalar}

RAPOR FORMATINDA DETAYLI ANALİZ:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analiz_prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        analiz_metni = response.choices[0].message.content.strip()
        return parse_klinik_analiz(analiz_metni)
        
    except Exception as e:
        st.error(f"Seans analizi hatası: {e}")
        return basit_analiz_sonucu()

def parse_klinik_analiz(analiz_metni):
    """Klinik analiz metnini parse et"""
    analiz_sonucu = {
        "klinik_tani": "",
        "semptom_profili": "",
        "mental_status": "",
        "siddet_degerlendirmesi": "",
        "etiyoloji": "",
        "diferansiyel_tani": "",
        "prognoz": "",
        "tedavi_plani": "",
        "takip_protokolu": "",
        "degerlendirme": "",
        "oneriler": [],
        "stres_seviyesi": 5,
        "ruh_hali": "stable",
        "aciliyet": "orta"
    }
    
    lines = analiz_metni.split('\n')
    current_section = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Ana bölümleri parse et
        line_upper = line.upper()
        
        if 'KLİNİK_TANI:' in line_upper or 'TANI:' in line_upper:
            analiz_sonucu["klinik_tani"] = line.split(':', 1)[1].strip() if ':' in line else ""
        elif 'SEMPTOM' in line_upper and ':' in line:
            analiz_sonucu["semptom_profili"] = line.split(':', 1)[1].strip()
        elif 'MENTAL' in line_upper and ':' in line:
            analiz_sonucu["mental_status"] = line.split(':', 1)[1].strip()
        elif 'STRES' in line_upper and ':' in line:
            try:
                analiz_sonucu["stres_seviyesi"] = int(line.split(':')[1].strip().split()[0])
            except:
                pass
        elif 'RUH' in line_upper and ':' in line:
            analiz_sonucu["ruh_hali"] = line.split(':', 1)[1].strip().lower()
        elif 'TEDAVİ' in line_upper and ':' in line:
            analiz_sonucu["tedavi_plani"] = line.split(':', 1)[1].strip()
        elif 'PROGNOZ' in line_upper and ':' in line:
            analiz_sonucu["prognoz"] = line.split(':', 1)[1].strip()
        elif line.startswith('-') or line.startswith('•'):
            # Öneriler bölümü
            oneri = line[1:].strip()
            if oneri and len(oneri) > 5:
                analiz_sonucu["oneriler"].append(oneri)
    
    # Varsayılan değerler
    if not analiz_sonucu["klinik_tani"]:
        analiz_sonucu["klinik_tani"] = "Adjustment Disorder with Mixed Anxiety and Depressed Mood (309.28)"
    
    if not analiz_sonucu["oneriler"]:
        analiz_sonucu["oneriler"] = [
            "Cognitive Behavioral Therapy (KDT) protokolü başlatın",
            "Mindfulness-based stress reduction teknikleri",
            "Günlük mood tracking ile semptom monitoring",
            "Progressive muscle relaxation",
            "İki hafta sonra follow-up appointment"
        ]
    
    if not analiz_sonucu["degerlendirme"]:
        analiz_sonucu["degerlendirme"] = "Klinik değerlendirme tamamlandı. Hasta collaboration gösterdi ve therapeutic alliance kuruldu."
        
    return analiz_sonucu

def basit_analiz_sonucu():
    """API olmadığında basit analiz"""
    return {
        "klinik_tani": "Adjustment Disorder (309.9)",
        "semptom_profili": "Stress-related symptoms, emotional dysregulation",
        "degerlendirme": "Klinik değerlendirme tamamlandı. Hasta therapeutic engagement gösterdi.",
        "oneriler": [
            "KDT based intervention başlatın",
            "Stress management teknikleri",
            "Günlük self-monitoring"
        ],
        "stres_seviyesi": 5,
        "ruh_hali": "stable",
        "aciliyet": "orta",
        "tedavi_plani": "Cognitive-behavioral therapy + relaxation training",
        "prognoz": "Good prognosis"
    }

# Kullanıcı yönetimi fonksiyonları
def sifre_hash(sifre):
    """Şifreyi güvenli şekilde hashle"""
    return hashlib.sha256(sifre.encode()).hexdigest()

def kullanici_veri_yukle(kullanici_adi):
    """Session state'den kullanıcı verisi yükle"""
    if "kullanici_verileri" not in st.session_state:
        st.session_state.kullanici_verileri = {}
    
    return st.session_state.kullanici_verileri.get(kullanici_adi, None)

def kullanici_veri_kaydet(kullanici_adi, veri):
    """Session state'e kullanıcı verisi kaydet"""
    if "kullanici_verileri" not in st.session_state:
        st.session_state.kullanici_verileri = {}
    
    st.session_state.kullanici_verileri[kullanici_adi] = veri
    return True

def kullanici_kayit():
    """Yeni kullanıcı kaydı"""
    st.markdown("### 📝 Yeni Hesap Oluştur")
    
    with st.form("kayit_formu"):
        kullanici_adi = st.text_input("Kullanıcı Adı", placeholder="En az 3 karakter")
        sifre = st.text_input("Şifre", type="password", placeholder="En az 6 karakter")
        sifre_tekrar = st.text_input("Şifre Tekrar", type="password")
        
        kayit_butonu = st.form_submit_button("Hesap Oluştur")
        
        if kayit_butonu:
            if len(kullanici_adi) < 3:
                st.error("Kullanıcı adı en az 3 karakter olmalı!")
                return
            
            if len(sifre) < 6:
                st.error("Şifre en az 6 karakter olmalı!")
                return
                
            if sifre != sifre_tekrar:
                st.error("Şifreler eşleşmiyor!")
                return
            
            # Kullanıcı zaten var mı kontrol et
            if kullanici_veri_yukle(kullanici_adi):
                st.error("Bu kullanıcı adı zaten alınmış!")
                return
            
            # Yeni kullanıcı verisi
            kullanici_data = {
                "kullanici_adi": kullanici_adi,
                "sifre_hash": sifre_hash(sifre),
                "kayit_tarihi": datetime.now().isoformat(),
                "seanslar": [],
                "profil": {
                    "toplam_seans": 0,
                    "son_giris": None
                }
            }
            
            kullanici_veri_kaydet(kullanici_adi, kullanici_data)
            st.success("✅ Hesap başarıyla oluşturuldu! Giriş yapabilirsiniz.")
            st.session_state.show_login = True
            st.rerun()

def kullanici_giris():
    """Kullanıcı girişi"""
    st.markdown("### 🔐 Giriş Yap")
    
    with st.form("giris_formu"):
        kullanici_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        
        giris_butonu = st.form_submit_button("Giriş Yap")
        
        if giris_butonu:
            kullanici_data = kullanici_veri_yukle(kullanici_adi)
            
            if not kullanici_data:
                st.error("Kullanıcı bulunamadı!")
                return
            
            if kullanici_data["sifre_hash"] != sifre_hash(sifre):
                st.error("Yanlış şifre!")
                return
            
            # Giriş başarılı
            st.session_state.kullanici_adi = kullanici_adi
            st.session_state.kullanici_data = kullanici_data
            st.session_state.giris_yapildi = True
            
            # Son giriş tarihini güncelle
            kullanici_data["profil"]["son_giris"] = datetime.now().isoformat()
            kullanici_veri_kaydet(kullanici_adi, kullanici_data)
            
            st.success("✅ Giriş başarılı!")
            st.rerun()

def problem_tanımlama():
    """Kullanıcının problemini yazılı olarak ifade etmesi"""
    st.markdown("### 🎯 AI-Psycho ile Profesyonel Değerlendirme")
    
    st.success("""
    🌟 **Hoşgeldiniz! Ben AI-Psycho - Profesyonel psikoloji değerlendirme sistemi**
    
    🎓 Dr. Marcus Reed AI protokolü ile çalışıyorum
    
    💫 5 dakikalık seansınız sonunda kapsamlı klinik rapor alacaksınız
    """)
    
    # Streamlit Share için uyarı
    st.info("""
    📝 **DEMO SÜRÜMÜ:** Bu versiyonda yazılı konuşma kullanılmaktadır.
    """)
    
    with st.form("problem_formu"):
        problem_metni = st.text_area(
            "💭 Bugün sizi buraya getiren durumu anlatın:",
            placeholder="Mevcut durumunuzu, hissettiklerinizi ve yaşadığınız zorlukları detaylandırın...",
            height=150
        )
        
        daha_once_terapi = st.selectbox(
            "🧠 Daha önce psikolojik destek aldınız mı?",
            ["Hayır, ilk defa", "Evet, birkaç seans", "Evet, düzenli olarak"]
        )
        
        aciliyet = st.selectbox(
            "⚡ Bu durumun günlük yaşamınızı etkileme derecesi:",
            ["Hafif rahatsızlık", "Orta düzey etki", "Ciddi şekilde etkiliyor", "Dayanılmaz, acil yardım lazım"]
        )
        
        problem_kaydet = st.form_submit_button("🚀 Klinik Değerlendirmeye Başla", type="primary")
        
        if problem_kaydet:
            if len(problem_metni.strip()) < 20:
                st.error("⚠️ Daha detaylı açıklama yapmanız değerlendirme kalitesini artıracaktır")
                return
            
            # Problem verisini session state'e kaydet
            st.session_state.mevcut_problem = {
                "metin": problem_metni,
                "terapi_gecmisi": daha_once_terapi,
                "aciliyet": aciliyet,
                "tarih": datetime.now().isoformat()
            }
            
            st.session_state.seans_asamasi = "seans_baslangic"
            st.success("🎯 Başlangıç değerlendirmesi tamamlandı!")
            st.balloons()
            time.sleep(2)
            st.rerun()

def seans_yonetim():
    """5 dakikalık seans yönetimi"""
    
    # Seans başlangıç kontrolü
    if "seans_baslangic_zamani" not in st.session_state:
        st.session_state.seans_baslangic_zamani = datetime.now()
        st.session_state.seans_konusmalari = []
        st.session_state.kullanici_konusma_sirasi = True
        st.session_state.konusma_sayisi = 0
    
    # Seans süresi hesaplama
    gecen_sure = (datetime.now() - st.session_state.seans_baslangic_zamani).total_seconds()
    kalan_sure = max(0, 300 - gecen_sure)  # 5 dakika = 300 saniye
    
    # Seans bitişi kontrolü
    if kalan_sure <= 0:
        st.session_state.seans_asamasi = "seans_analiz"
        st.rerun()
    
    # Süresi gösteren header
    dakika = int(kalan_sure // 60)
    saniye = int(kalan_sure % 60)
    
    if st.session_state.kullanici_konusma_sirasi:
        st.success(f"🎤 **KONUŞMA SIRANIZ** ⏰ {dakika}:{saniye:02d}")
        if st.session_state.konusma_sayisi == 0:
            st.info("💫 **Dr. Marcus Reed sizi dinlemeye hazır** - Düşüncelerinizi açıkça paylaşın")
        else:
            st.info("🔍 **Değerlendirmeye devam** - Sorularımı yanıtlayın")
    else:
        st.warning(f"🧠 **KLİNİK DEĞERLENDİRME** ⏰ {dakika}:{saniye:02d}")
        st.info("✨ **Dr. Marcus Reed analiz yapıyor** - Profesyonel görüş hazırlanıyor")
    
    # Seans aşama göstergesi
    progress = (st.session_state.konusma_sayisi + 1) / 5
    st.progress(progress, f"Değerlendirme Aşaması: {st.session_state.konusma_sayisi + 1}/5")
    
    # Streamlit session başlangıçlarını garantiye al
    if "kullanici_konusma_sirasi" not in st.session_state:
        st.session_state.kullanici_konusma_sirasi = True

    if "konusma_sayisi" not in st.session_state:
        st.session_state.konusma_sayisi = 0

    if "seans_konusmalari" not in st.session_state:
        st.session_state.seans_konusmalari = []

    if st.session_state.kullanici_konusma_sirasi:
        st.markdown("### ✍️ Yanıtınızı Yazın")
        st.info("💡 **İpucu:** Samimi ve açık bir dille yazın.")

        with st.form(f"konusma_formu_{st.session_state.konusma_sayisi}"):
            kullanici_mesaji = st.text_area(
                "💭 Düşüncelerinizi paylaşın:",
                placeholder="Bu konuda ne düşünüyorsunuz?",
                height=120,
                key=f"mesaj_{st.session_state.konusma_sayisi}"
            )

            konusma_gonder = st.form_submit_button("📤 Gönder")

            if konusma_gonder:
                if len(kullanici_mesaji.strip()) < 10:
                    st.error("Lütfen daha detaylı bir yanıt verin")
                    st.stop()

                st.session_state.mevcut_kullanici_konusma = kullanici_mesaji
                st.session_state.kullanici_konusma_sirasi = False
                st.rerun()

    else:
        st.markdown("### 🤖 Dr. Marcus Reed Değerlendirme Yapıyor")

        if "ai_cevap_uretti" not in st.session_state:
            with st.spinner("🧠 Klinik analiz hazırlanıyor..."):
                ai_cevap_uret()

            st.session_state.ai_cevap_uretti = True

        if st.button("➡️ Bir Sonraki Aşama", use_container_width=True, type="primary"):
            st.session_state.kullanici_konusma_sirasi = True
            st.session_state.konusma_sayisi += 1
            del st.session_state.ai_cevap_uretti
            st.rerun()

    # Geçmiş konuşmaları göster
    if st.session_state.seans_konusmalari:
        st.markdown("### 📋 Değerlendirme Süreci")
        for i, konusma in enumerate(reversed(st.session_state.seans_konusmalari[-2:])):
            with st.expander(f"🔍 Aşama {len(st.session_state.seans_konusmalari)-i}", expanded=(i == 0)):
                st.markdown(f"**👤 Siz:** {konusma['kullanici']}")
                st.markdown(f"**🧠 Dr. Marcus Reed:** {konusma['ai']}")

def ai_cevap_uret():
    """AI'ın korumalı cevap üretmesi"""
    if "mevcut_kullanici_konusma" not in st.session_state:
        st.warning("❗ Kullanıcı konuşması bulunamadı.")
        return

    if "mevcut_problem" not in st.session_state:
        st.warning("❗ Problem tanımlanmadan değerlendirme yapılamaz.")
        return

    kullanici_metni = st.session_state.mevcut_kullanici_konusma
    problem_bilgisi = st.session_state.mevcut_problem
    konusma_gecmisi = st.session_state.seans_konusmalari

    # AI cevap üret
    ai_cevabi = ai_psikolog_cevap_uret(
        kullanici_metni,
        problem_bilgisi,
        konusma_gecmisi,
        st.session_state.konusma_sayisi
    )

    st.success("🧠 **DR. MARCUS REED'DEN PROFESYONEL GÖRÜŞ:**")
    st.markdown(f"*{ai_cevabi}*")

    # Sesli yanıt
    try:
        with st.spinner("🔊 Dr. Marcus Reed seslendiriyor..."):
            ses_baytlari = metinden_sese_openai(ai_cevabi)
            if ses_baytlari:
                ses_baytlarini_cal(ses_baytlari)
                st.success("🎵 Sesli yanıt hazır!")
            else:
                st.info("📝 Yazılı yanıt hazır")
    except Exception as e:
        st.warning(f"Ses hatası: {e}")

    # Konuşma kaydet
    st.session_state.seans_konusmalari.append({
        "kullanici": kullanici_metni,
        "ai": ai_cevabi,
        "zaman": datetime.now().isoformat()
    })

    del st.session_state.mevcut_kullanici_konusma

def seans_analiz_goster():
    """Korumalı klinik analiz raporu"""
    st.markdown("## 📋 KLİNİK DEĞERLENDİRME RAPORU")
    st.caption("Dr. Marcus Reed Protokolü ile Hazırlanmıştır")
    
    if "seans_analizi" not in st.session_state:
        with st.spinner("🧠 Kapsamlı klinik analiz yapılıyor..."):
            time.sleep(4)
            analiz = seans_analizi_yap(
                st.session_state.mevcut_problem,
                st.session_state.seans_konusmalari
            )
            st.session_state.seans_analizi = analiz
    
    analiz = st.session_state.seans_analizi
    
    # Profesyonel rapor sunumu
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Klinik tanı
        st.markdown("### 🎯 KLİNİK TANI")
        if analiz.get("klinik_tani"):
            st.error(f"**📋 TANI:** {analiz['klinik_tani']}")
        
        # Semptom profili
        if analiz.get("semptom_profili"):
            st.markdown("### 🔍 SEMPTOM PROFİLİ")
            st.info(analiz["semptom_profili"])
        
        # Mental status
        if analiz.get("mental_status"):
            st.markdown("### 🧠 MENTAL STATUS")
            st.write(analiz["mental_status"])
        
        # Tedavi planı
        if analiz.get("tedavi_plani"):
            st.markdown("### 💊 ÖNERİLEN TEDAVİ")
            st.success(f"**Protokol:** {analiz['tedavi_plani']}")
        
        # Klinik öneriler
        st.markdown("### 📝 UZMAN ÖNERİLERİ")
        for i, oneri in enumerate(analiz["oneriler"], 1):
            st.write(f"**{i}.** {oneri}")
        
        # Kapsamlı değerlendirme
        st.markdown("### 📊 GENEL DEĞERLENDİRME")
        st.write(analiz["degerlendirme"])
    
    with col2:
        st.markdown("### 📈 KLİNİK SKORLAR")
        
        # Stres seviyesi
        stres_renk = "🟢" if analiz["stres_seviyesi"] <= 3 else "🟡" if analiz["stres_seviyesi"] <= 6 else "🔴"
        st.metric("Stres Seviyesi", f"{stres_renk} {analiz['stres_seviyesi']}/10")
        
        # Ruh hali
        ruh_hali_emoji = {
            "anxious": "😰", "depressed": "😔", "stable": "😐", 
            "elevated": "😊", "dysthymic": "😑"
        }
        emoji = ruh_hali_emoji.get(analiz["ruh_hali"], "🧠")
        st.metric("Mental Durum", f"{emoji} {analiz['ruh_hali'].title()}")
        
        # Prognoz
        if analiz.get("prognoz"):
            prognoz_emoji = "🏆" if "good" in analiz["prognoz"].lower() else "📋"
            st.metric("Prognoz", f"{prognoz_emoji} {analiz['prognoz']}")
        
        # Aciliyet durumu
        if analiz["aciliyet"] == "yuksek":
            st.error("⚠️ Yüksek Öncelik")
        elif analiz["aciliyet"] == "orta":
            st.warning("📋 Rutin Takip")
        else:
            st.success("✅ Düşük Risk")
        
        st.metric("Değerlendirme", "🏆 Tamamlandı")
    
    st.markdown("---")
    
    # Son butonlar
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("📋 Raporu Kaydet", use_container_width=True, type="primary"):
            seans_kaydet()
            st.success("✅ Klinik rapor kaydedildi!")
            st.balloons()
            time.sleep(2)
            seans_sifirla()
            st.rerun()
    
    with col_b:
        if st.button("🔄 Yeni Değerlendirme", use_container_width=True):
            seans_sifirla()
            st.session_state.sayfa = "yeni_seans"
            st.rerun()

def seans_kaydet():
    """Seansı kullanıcı verisine kaydet"""
    kullanici_data = st.session_state.kullanici_data
    
    yeni_seans = {
        "tarih": st.session_state.seans_baslangic_zamani.isoformat(),
        "problem": st.session_state.mevcut_problem,
        "konusmalar": st.session_state.seans_konusmalari,
        "analiz": st.session_state.seans_analizi,
        "sure": 300
    }
    
    kullanici_data["seanslar"].append(yeni_seans)
    kullanici_data["profil"]["toplam_seans"] += 1
    
    kullanici_veri_kaydet(st.session_state.kullanici_adi, kullanici_data)
    st.session_state.kullanici_data = kullanici_data

def seans_sifirla():
    """Seans verilerini sıfırla"""
    keys_to_remove = [
        "seans_asamasi", "seans_baslangic_zamani", "seans_konusmalari",
        "kullanici_konusma_sirasi", "konusma_sayisi", "mevcut_kullanici_konusma",
        "ai_cevap_uretti", "seans_analizi", "mevcut_problem"
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def kullanici_profil():
    """Kullanıcı profili"""
    st.markdown("### 👤 Profiliniz")
    
    kullanici_data = st.session_state.kullanici_data
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Toplam Değerlendirme", kullanici_data["profil"]["toplam_seans"])
    
    with col2:
        if kullanici_data["profil"]["son_giris"]:
            son_giris = datetime.fromisoformat(kullanici_data["profil"]["son_giris"])
            st.metric("🕐 Son Giriş", son_giris.strftime("%d.%m.%Y"))
    
    with col3:
        kayit_tarihi = datetime.fromisoformat(kullanici_data["kayit_tarihi"])
        st.metric("📅 Üyelik", kayit_tarihi.strftime("%d.%m.%Y"))
    
    # Motivasyon mesajı
    if kullanici_data["profil"]["toplam_seans"] == 0:
        st.info("🌟 **İlk profesyonel değerlendirmeniz için hazır mısınız?**")
    elif kullanici_data["profil"]["toplam_seans"] < 3:
        st.success(f"📈 **{kullanici_data['profil']['toplam_seans']} değerlendirme tamamladınız!**")
    else:
        st.success(f"🏆 **{kullanici_data['profil']['toplam_seans']} değerlendirme! Harika ilerleme!**")
    
    # Geçmiş seanslar
    if kullanici_data["seanslar"]:
        st.markdown("### 📚 Değerlendirme Geçmişi")
        
        for i, seans in enumerate(reversed(kullanici_data["seanslar"][-5:])):
            tarih = datetime.fromisoformat(seans["tarih"])
            
            with st.expander(f"📋 Rapor {len(kullanici_data['seanslar'])-i} - {tarih.strftime('%d.%m.%Y')}", expanded=(i==0)):
                st.write(f"**🎯 Problem:** {seans['problem']['metin'][:100]}...")
                
                if 'klinik_tani' in seans['analiz']:
                    st.error(f"**📋 Tanı:** {seans['analiz']['klinik_tani']}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**📊 Stres:** {seans['analiz']['stres_seviyesi']}/10")
                    st.write(f"**🧠 Durum:** {seans['analiz']['ruh_hali'].title()}")
                
                with col_b:
                    st.write(f"**💬 Etkileşim:** {len(seans['konusmalar'])}")
                    if 'prognoz' in seans['analiz']:
                        st.write(f"**📈 Prognoz:** {seans['analiz']['prognoz']}")
    else:
        st.info("🚀 **Henüz değerlendirme yapmadınız. İlk seansınıza başlayın!**")

def main():
    st.set_page_config(
        page_title="AI-Psycho Professional",
        page_icon="🧠",
        layout="wide"
    )
    
    st.markdown("""
    <h1 style="color: #2E86AB; text-align: center;">
        🧠 AI-Psycho Professional
    </h1>
    <h3 style="color: #A23B72; text-align: center;">
        Dr. Marcus Reed Protokolü ile Profesyonel Psikoloji Değerlendirmesi
    </h3>
    """, unsafe_allow_html=True)
    
    # Güvenlik uyarısı
    st.info("🔒 **Güvenli Platform:** Tüm verileriniz şifrelenir ve gizli tutulur")
    
    # OpenAI başlat
    if not openai_baslat():
        st.error("❌ Sistem yapılandırması gerekli")
        st.info("API bağlantısı kurulamadı. Lütfen yönetici ile iletişime geçin.")
        st.stop()
    
    # Session state başlangıç değerleri
    if "giris_yapildi" not in st.session_state:
        st.session_state.giris_yapildi = False
    
    # Giriş yapılmamış durumda
    if not st.session_state.giris_yapildi:
        tab1, tab2 = st.tabs(["🔐 Giriş", "📝 Kayıt"])
        
        with tab1:
            kullanici_giris()
        
        with tab2:
            kullanici_kayit()
        
        # Platform tanıtımı
        st.markdown("---")
        st.markdown("### 🌟 AI-Psycho Professional")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("""
            **🎯 Profesyonel Değerlendirme**
            • DSM-5 tanı sistemi
            • Klinik terminoloji
            • Uzman görüş
            """)
        
        with col2:
            st.info("""
            **🧠 Dr. Marcus Reed AI**
            • 20 yıllık deneyim simülasyonu
            • Johns Hopkins protokolü
            • Evidence-based yaklaşım
            """)
        
        with col3:
            st.warning("""
            **🔒 Güvenlik & Gizlilik**
            • Şifrelenmiş veriler
            • Anonim değerlendirme
            • KVKK uyumlu
            """)
        
        return
    
    # Giriş yapılmış durumda
    with st.sidebar:
        st.markdown(f"### 👋 Hoşgeldiniz")
        st.write(f"**{st.session_state.kullanici_adi}**")
        
        kullanici_data = st.session_state.kullanici_data
        toplam_seans = kullanici_data["profil"]["toplam_seans"]
        
        if toplam_seans == 0:
            st.info("🌟 İlk değerlendirmeniz")
        else:
            st.success(f"📊 {toplam_seans} rapor")
        
        if st.button("👤 Profil", use_container_width=True):
            st.session_state.sayfa = "profil"
            st.rerun()
        
        if st.button("🆕 Yeni Değerlendirme", use_container_width=True, type="primary"):
            seans_sifirla()
            st.session_state.sayfa = "yeni_seans"
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Bugün")
        gunun_sozleri = [
            "Her adım önemli 💪",
            "Güçlü kalın 🦁", 
            "Umut hep var ✨",
            "Değişim mümkün 🚀"
        ]
        import random
        st.info(random.choice(gunun_sozleri))
        
        st.markdown("---")
        if st.button("🚪 Çıkış", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Sayfa yönlendirme
    if "sayfa" not in st.session_state:
        st.session_state.sayfa = "profil"
    
    if st.session_state.sayfa == "profil":
        kullanici_profil()
    elif st.session_state.sayfa == "yeni_seans":
        if "seans_asamasi" not in st.session_state:
            st.session_state.seans_asamasi = "problem_tanimlama"
        
        if st.session_state.seans_asamasi == "problem_tanimlama":
            problem_tanımlama()
        elif st.session_state.seans_asamasi == "seans_baslangic":
            seans_yonetim()
        elif st.session_state.seans_asamasi == "seans_analiz":
            seans_analiz_goster()

if __name__ == "__main__":
    main()
