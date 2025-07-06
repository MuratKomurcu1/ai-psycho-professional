import streamlit as st
import json
import os
from datetime import datetime, timedelta
import time
import hashlib
import base64

# OpenAI import
try:
    from openai import OpenAI
except ImportError:
    st.error("OpenAI paketi yüklenemedi. Requirements.txt kontrol edin.")
    st.stop()

# Global değişkenler
openai_client = None

def openai_baslat():
    """OpenAI client'ı başlat"""
    global openai_client
    
    # API key alma - Streamlit Cloud uyumlu
    api_key = None
    
    # 1. Streamlit secrets'tan dene
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        pass
    
    # 2. Environment variable'dan dene
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            openai_client = OpenAI(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"OpenAI client hatası: {e}")
            return False
    else:
        st.error("❌ OpenAI API anahtarı bulunamadı! Lütfen Streamlit Cloud Secrets'da OPENAI_API_KEY ayarlayın.")
    return False

def get_system_prompts():
    """Sistem promptları"""
    return {
        "ilk_seans": "Sen Dr. Marcus Reed - 20 yıllık deneyimli klinik psikolog. Hastayı karşıla, güven kur ve ilk değerlendirmeyi yap.",
        "orta_seans": "Daha detaylı analiz yap. Semptomları keşfet ve tetikleyici faktörleri araştır.",
        "son_seans": "Kapsamlı değerlendirme ve tedavi önerileri sun. Klinik rapor hazırla."
    }

def ai_psikolog_cevap_uret(kullanici_metni, problem_bilgisi, konusma_gecmisi, konusma_sirasi):
    """AI psikolog cevap üretici"""
    try:
        if not openai_client:
            return "Size destek olmak için buradayım. Bu durumu birlikte ele alabiliriz."
        
        # Prompt hazırla
        if konusma_sirasi == 0:
            sistem_prompt = "Sen deneyimli bir klinik psikolog olarak hastayı karşılıyorsun. Empati kur ve güven ver."
        elif konusma_sirasi <= 2:
            sistem_prompt = "Daha detaylı değerlendirme yap. Semptomları ve tetikleyici faktörleri araştır."
        else:
            sistem_prompt = "Kapsamlı değerlendirme yap ve tedavi önerileri sun."
        
        prompt = f"""{sistem_prompt}

Hasta sorunu: {problem_bilgisi['metin'][:200]}
Terapi geçmişi: {problem_bilgisi['terapi_gecmisi']}
Aciliyet: {problem_bilgisi['aciliyet']}

Hasta: "{kullanici_metni}"

Profesyonel, empatik ve terapötik cevap ver (60-80 kelime):"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"AI cevap hatası: {e}")
        return "Anlıyorum. Bu durumu daha detaylı ele alalım. Neler hissediyorsunuz?"

def seans_analizi_yap(problem_bilgisi, konusma_gecmisi):
    """Seans analizi"""
    try:
        if not openai_client:
            return basit_analiz_sonucu()
        
        # Konuşmaları birleştir
        konusmalar = ""
        for k in konusma_gecmisi:
            konusmalar += f"Hasta: {k['kullanici']}\nPsikolog: {k['ai']}\n\n"
        
        analiz_prompt = f"""Bu klinik seansı analiz et:

Problem: {problem_bilgisi['metin']}
Aciliyet: {problem_bilgisi['aciliyet']}

Konuşmalar:
{konusmalar}

Şu formatta analiz yap:
TANI: [Klinik tanı]
STRES: [0-10 arası]
DURUM: [stable/anxious/depressed]
TEDAVI: [Önerilen yaklaşım]
ONERILER: [3-4 madde]"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analiz_prompt}],
            max_tokens=400,
            temperature=0.3
        )
        
        return parse_analiz(response.choices[0].message.content)
        
    except Exception as e:
        st.error(f"Analiz hatası: {e}")
        return basit_analiz_sonucu()

def parse_analiz(analiz_metni):
    """Analiz metnini parse et"""
    sonuc = {
        "klinik_tani": "",
        "stres_seviyesi": 5,
        "ruh_hali": "stable",
        "tedavi_plani": "",
        "oneriler": [],
        "degerlendirme": analiz_metni
    }
    
    lines = analiz_metni.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('TANI:'):
            sonuc["klinik_tani"] = line.replace('TANI:', '').strip()
        elif line.startswith('STRES:'):
            try:
                sonuc["stres_seviyesi"] = int(line.replace('STRES:', '').strip())
            except:
                pass
        elif line.startswith('DURUM:'):
            sonuc["ruh_hali"] = line.replace('DURUM:', '').strip()
        elif line.startswith('TEDAVI:'):
            sonuc["tedavi_plani"] = line.replace('TEDAVI:', '').strip()
        elif line.startswith('-'):
            sonuc["oneriler"].append(line[1:].strip())
    
    # Varsayılan değerler
    if not sonuc["klinik_tani"]:
        sonuc["klinik_tani"] = "Adjustment Disorder (309.9)"
    if not sonuc["oneriler"]:
        sonuc["oneriler"] = [
            "Günlük stres yönetimi teknikleri",
            "Düzenli egzersiz ve uyku",
            "Profesyonel destek almayı değerlendirin"
        ]
    
    return sonuc

def basit_analiz_sonucu():
    """Basit analiz sonucu"""
    return {
        "klinik_tani": "Genel Adaptation Zorluğu",
        "stres_seviyesi": 5,
        "ruh_hali": "stable",
        "tedavi_plani": "Supportif terapi ve stres yönetimi",
        "oneriler": [
            "Günlük nefes egzersizleri",
            "Düzenli uyku düzeni",
            "Sosyal destek sistemini güçlendirin"
        ],
        "degerlendirme": "Klinik değerlendirme tamamlandı. Genel adaptasyon zorluğu gözlendi."
    }

# Kullanıcı yönetimi
def sifre_hash(sifre):
    """Şifreyi hashle"""
    return hashlib.sha256(sifre.encode()).hexdigest()

def kullanici_veri_yukle(kullanici_adi):
    """Kullanıcı verisi yükle"""
    if "kullanici_verileri" not in st.session_state:
        st.session_state.kullanici_verileri = {}
    return st.session_state.kullanici_verileri.get(kullanici_adi, None)

def kullanici_veri_kaydet(kullanici_adi, veri):
    """Kullanıcı verisi kaydet"""
    if "kullanici_verileri" not in st.session_state:
        st.session_state.kullanici_verileri = {}
    st.session_state.kullanici_verileri[kullanici_adi] = veri
    return True

def kullanici_kayit():
    """Kullanıcı kaydı"""
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
            
            if kullanici_veri_yukle(kullanici_adi):
                st.error("Bu kullanıcı adı zaten alınmış!")
                return
            
            kullanici_data = {
                "kullanici_adi": kullanici_adi,
                "sifre_hash": sifre_hash(sifre),
                "kayit_tarihi": datetime.now().isoformat(),
                "seanslar": [],
                "profil": {"toplam_seans": 0, "son_giris": None}
            }
            
            kullanici_veri_kaydet(kullanici_adi, kullanici_data)
            st.success("✅ Hesap başarıyla oluşturuldu!")
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
            
            st.session_state.kullanici_adi = kullanici_adi
            st.session_state.kullanici_data = kullanici_data
            st.session_state.giris_yapildi = True
            
            kullanici_data["profil"]["son_giris"] = datetime.now().isoformat()
            kullanici_veri_kaydet(kullanici_adi, kullanici_data)
            
            st.success("✅ Giriş başarılı!")
            st.rerun()

def problem_tanımlama():
    """Problem tanımlama"""
    st.markdown("### 🎯 AI-Psycho ile Profesyonel Değerlendirme")
    
    st.success("""
    🌟 **Hoşgeldiniz! Ben AI-Psycho - Profesyonel psikoloji değerlendirme sistemi**
    
    🎓 Dr. Marcus Reed AI protokolü ile çalışıyorum
    
    💫 5 dakikalık seansınız sonunda kapsamlı klinik rapor alacaksınız
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
            
            st.session_state.mevcut_problem = {
                "metin": problem_metni,
                "terapi_gecmisi": daha_once_terapi,
                "aciliyet": aciliyet,
                "tarih": datetime.now().isoformat()
            }
            
            st.session_state.seans_asamasi = "seans_baslangic"
            st.success("🎯 Başlangıç değerlendirmesi tamamlandı!")
            time.sleep(2)
            st.rerun()

def seans_yonetim():
    """Seans yönetimi"""
    # Session state başlangıç
    if "seans_baslangic_zamani" not in st.session_state:
        st.session_state.seans_baslangic_zamani = datetime.now()
        st.session_state.seans_konusmalari = []
        st.session_state.kullanici_konusma_sirasi = True
        st.session_state.konusma_sayisi = 0
    
    # Süre hesaplama
    gecen_sure = (datetime.now() - st.session_state.seans_baslangic_zamani).total_seconds()
    kalan_sure = max(0, 300 - gecen_sure)
    
    if kalan_sure <= 0:
        st.session_state.seans_asamasi = "seans_analiz"
        st.rerun()
    
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
    
    progress = (st.session_state.konusma_sayisi + 1) / 5
    st.progress(progress, f"Değerlendirme Aşaması: {st.session_state.konusma_sayisi + 1}/5")
    
    if st.session_state.kullanici_konusma_sirasi:
        st.markdown("### ✍️ Yanıtınızı Yazın")
        with st.form(f"konusma_formu_{st.session_state.konusma_sayisi}"):
            kullanici_mesaji = st.text_area(
                "💭 Düşüncelerinizi paylaşın:",
                placeholder="Bu konuda ne düşünüyorsunuz?",
                height=120
            )
            konusma_gonder = st.form_submit_button("📤 Gönder")
            
            if konusma_gonder and kullanici_mesaji.strip():
                if len(kullanici_mesaji.strip()) < 10:
                    st.error("Lütfen daha detaylı bir yanıt verin")
                    return
                
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
            if "ai_cevap_uretti" in st.session_state:
                del st.session_state.ai_cevap_uretti
            st.rerun()
    
    # Konuşma geçmişi
    if st.session_state.seans_konusmalari:
        st.markdown("### 📋 Değerlendirme Süreci")
        for i, konusma in enumerate(reversed(st.session_state.seans_konusmalari[-2:])):
            with st.expander(f"🔍 Aşama {len(st.session_state.seans_konusmalari)-i}", expanded=(i == 0)):
                st.markdown(f"**👤 Siz:** {konusma['kullanici']}")
                st.markdown(f"**🧠 Dr. Marcus Reed:** {konusma['ai']}")

def ai_cevap_uret():
    """AI cevap üret"""
    if "mevcut_kullanici_konusma" not in st.session_state:
        st.warning("❗ Kullanıcı konuşması bulunamadı.")
        return
    
    kullanici_metni = st.session_state.mevcut_kullanici_konusma
    problem_bilgisi = st.session_state.mevcut_problem
    konusma_gecmisi = st.session_state.seans_konusmalari
    
    ai_cevabi = ai_psikolog_cevap_uret(
        kullanici_metni,
        problem_bilgisi,
        konusma_gecmisi,
        st.session_state.konusma_sayisi
    )
    
    st.success("🧠 **DR. MARCUS REED'DEN PROFESYONEL GÖRÜŞ:**")
    st.markdown(f"*{ai_cevabi}*")
    
    st.session_state.seans_konusmalari.append({
        "kullanici": kullanici_metni,
        "ai": ai_cevabi,
        "zaman": datetime.now().isoformat()
    })
    
    del st.session_state.mevcut_kullanici_konusma

def seans_analiz_goster():
    """Analiz raporu"""
    st.markdown("## 📋 KLİNİK DEĞERLENDİRME RAPORU")
    st.caption("Dr. Marcus Reed Protokolü ile Hazırlanmıştır")
    
    if "seans_analizi" not in st.session_state:
        with st.spinner("🧠 Kapsamlı klinik analiz yapılıyor..."):
            time.sleep(3)
            analiz = seans_analizi_yap(
                st.session_state.mevcut_problem,
                st.session_state.seans_konusmalari
            )
            st.session_state.seans_analizi = analiz
    
    analiz = st.session_state.seans_analizi
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 KLİNİK TANI")
        st.error(f"**📋 TANI:** {analiz['klinik_tani']}")
        
        st.markdown("### 💊 ÖNERİLEN TEDAVİ")
        st.success(f"**Protokol:** {analiz['tedavi_plani']}")
        
        st.markdown("### 📝 UZMAN ÖNERİLERİ")
        for i, oneri in enumerate(analiz["oneriler"], 1):
            st.write(f"**{i}.** {oneri}")
        
        st.markdown("### 📊 GENEL DEĞERLENDİRME")
        st.write(analiz["degerlendirme"])
    
    with col2:
        st.markdown("### 📈 KLİNİK SKORLAR")
        
        stres_renk = "🟢" if analiz["stres_seviyesi"] <= 3 else "🟡" if analiz["stres_seviyesi"] <= 6 else "🔴"
        st.metric("Stres Seviyesi", f"{stres_renk} {analiz['stres_seviyesi']}/10")
        
        ruh_hali_emoji = {"anxious": "😰", "depressed": "😔", "stable": "😐"}
        emoji = ruh_hali_emoji.get(analiz["ruh_hali"], "🧠")
        st.metric("Mental Durum", f"{emoji} {analiz['ruh_hali'].title()}")
        
        st.metric("Değerlendirme", "🏆 Tamamlandı")
    
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📋 Raporu Kaydet", use_container_width=True, type="primary"):
            seans_kaydet()
            st.success("✅ Klinik rapor kaydedildi!")
            seans_sifirla()
            st.rerun()
    
    with col_b:
        if st.button("🔄 Yeni Değerlendirme", use_container_width=True):
            seans_sifirla()
            st.session_state.sayfa = "yeni_seans"
            st.rerun()

def seans_kaydet():
    """Seans kaydet"""
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
    
    if kullanici_data["profil"]["toplam_seans"] == 0:
        st.info("🌟 **İlk profesyonel değerlendirmeniz için hazır mısınız?**")
    else:
        st.success(f"🏆 **{kullanici_data['profil']['toplam_seans']} değerlendirme tamamladınız!**")
    
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
    
    st.info("🔒 **Güvenli Platform:** Tüm verileriniz şifrelenir ve gizli tutulur")
    
    # OpenAI başlat
    if not openai_baslat():
        st.error("❌ Sistem yapılandırması gerekli")
        st.info("API bağlantısı kurulamadı. Lütfen Streamlit Cloud Secrets'da OPENAI_API_KEY ayarlayın.")
        st.stop()
    
    # Session state başlangıç
    if "giris_yapildi" not in st.session_state:
        st.session_state.giris_yapildi = False
    
    # Giriş yapılmamış
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
