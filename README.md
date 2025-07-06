# 🧠 AI-Psycho Professional

> **Dr. Marcus Reed Protokolü ile Profesyonel Psikoloji Değerlendirme Sistemi**

AI-Psycho Professional, yapay zeka destekli klinik psikoloji değerlendirme platformudur. 20 yıllık deneyimli Dr. Marcus Reed protokolü ile çalışarak, kullanıcılara profesyonel düzeyde psikolojik analiz ve destek sunar.

![AI-Psycho Professional](https://img.shields.io/badge/AI-Psycho_Professional-blue?style=for-the-badge&logo=brain&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🌟 Özellikler

### 🎯 Klinik Değerlendirme
- **Dr. Marcus Reed AI Protokolü** - Johns Hopkins mezunu, 15.000+ hasta deneyimi
- **5 Dakikalık Klinik Seans** - Interaktif ve kapsamlı değerlendirme
- **DSM-5 Tanı Kriterleri** - Profesyonel klinik terminoloji
- **Diferansiyel Tanı Analizi** - Çoklu tanı seçenekleri değerlendirmesi

### 🛡️ Güvenlik & Gizlilik
- **Şifrelenmiş Veri Yönetimi** - Tüm hassas bilgiler korunur
- **Kullanıcı Kimlik Doğrulama** - Güvenli giriş/kayıt sistemi
- **Session-Based Storage** - Veriler güvenli oturumlarda saklanır
- **KVKK Uyumlu** - Veri koruma yasalarına tam uyum

### 🎨 Kullanıcı Deneyimi
- **Modern Web Arayüzü** - Streamlit ile optimize edilmiş
- **Sesli Yanıtlar** - OpenAI TTS ile doğal konuşma
- **Gerçek Zamanlı Analiz** - Anlık stres ve ruh hali tespiti
- **Kapsamlı Raporlama** - Detaylı klinik değerlendirme raporları

## 🚀 Demo

**Canlı Demo:** [ai-psycho-professional.streamlit.app](https://ai-psycho-professional.streamlit.app)

### 📱 Nasıl Kullanılır

1. **Hesap Oluşturun** - Güvenli kayıt sistemi
2. **Problem Tanımlayın** - Mevcut durumunuzu açıklayın
3. **5 Dakikalık Seans** - Dr. Marcus Reed ile interaktif değerlendirme
4. **Klinik Rapor** - Kapsamlı analiz ve öneriler alın

## 🛠️ Teknoloji Stack

- **🖥️ Frontend:** Streamlit
- **🤖 AI Engine:** OpenAI GPT-4o-mini
- **🔊 TTS:** OpenAI Text-to-Speech
- **🔐 Security:** Hashlib + Session Management
- **📊 Analytics:** Pandas + NumPy
- **☁️ Deployment:** Streamlit Cloud

## ⚙️ Kurulum

### Gereksinimler
- Python 3.8+
- OpenAI API Key
- Streamlit

### Yerel Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/MuratKomurcu1/ai-psycho-professional.git
cd ai-psycho-professional

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Environment variables ayarlayın
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Uygulamayı çalıştırın
streamlit run main.py
```

### Docker ile Kurulum

```bash
# Dockerfile oluşturun
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Build ve çalıştırın
docker build -t ai-psycho .
docker run -p 8501:8501 -e OPENAI_API_KEY=your-key ai-psycho
```

## 📁 Proje Yapısı

```
ai-psycho-professional/
├── main.py                 # Ana Streamlit uygulaması
├── requirements.txt        # Python bağımlılıkları
├── .env                   # Environment variables (local)
├── .gitignore            # Git ignore kuralları
├── utils_anxiety.py      # Yardımcı fonksiyonlar
├── config.py            # Yapılandırma dosyası
└── README.md           # Proje dökümantasyonu
```

## 🔧 Yapılandırma

### Environment Variables

```bash
# .env dosyası
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

### Streamlit Secrets (Production)

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

## 🧪 Kullanım Örnekleri

### Temel Kullanım

```python
# AI-Psycho Professional kullanımı
# 1. Hesap oluşturun veya giriş yapın
# 2. Problem tanımlama formunu doldurun
# 3. 5 dakikalık interaktif seansa katılın
# 4. Klinik raporu inceleyin ve kaydedin
```

### Değerlendirme Süreci

1. **İlk Görüşme (0-1 dk)** - Güven inşası ve semptom tespiti
2. **Orta Aşama (2-3 dk)** - Derin analiz ve diferansiyel tanı
3. **Son Aşama (4-5 dk)** - Kesin tanı ve tedavi protokolü
4. **Rapor (Otomatik)** - Kapsamlı klinik değerlendirme

## 📊 Sistem Özellikleri

### Klinik Analiz Kapasitesi
- ✅ **Anxiety Disorders** - GAD, Panic, Social Anxiety
- ✅ **Mood Disorders** - Depression, Bipolar, Dysthymia  
- ✅ **Stress-Related** - PTSD, Adjustment Disorders
- ✅ **Cognitive Issues** - Attention, Memory, Executive Function

### Güvenlik Standartları
- 🔐 **SHA-256 Encryption** - Şifre ve hassas veri koruması
- 🛡️ **Session Management** - Güvenli oturum yönetimi
- 🔒 **Data Privacy** - Veri minimizasyonu prensibi
- ⚡ **Real-time Processing** - Veriler kalıcı olarak saklanmaz

## 🤝 Katkıda Bulunma

1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'Add amazing feature'`)
4. **Branch'e push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## ⚠️ Yasal Uyarı

**Önemli:** AI-Psycho Professional bir destek aracıdır ve gerçek tıbbi/psikolojik danışmanlığın yerini alamaz. Acil durumlarda mutlaka profesyonel yardım alın.

### Acil Durum Kaynakları
- **Kriz Hattı:** 182
- **Hayat Hattı:** 444 0 682
- **TIHV:** 0312 310 6636
- **Ruh Sağlığı:** 444 6 334

## 👨‍💻 Geliştirici

**Murat Kömürcü**
- GitHub: [@MuratKomurcu1](https://github.com/MuratKomurcu1)
- Project: [AI-Psycho Professional](https://github.com/MuratKomurcu1/ai-psycho-professional)

## 🙏 Teşekkürler

- **OpenAI** - GPT-4 ve TTS hizmetleri için
- **Streamlit** - Harika web framework için
- **Python Community** - Açık kaynak kütüphaneler için

---

<div align="center">

**AI-Psycho Professional ile ruh sağlığınıza destek olun! 🧠✨**

[Demo Deneyin](https://ai-psycho-professional.streamlit.app) | [Sorun Bildirin](https://github.com/MuratKomurcu1/ai-psycho-professional/issues) | [Katkıda Bulunun](https://github.com/MuratKomurcu1/ai-psycho-professional/pulls)

</div>
