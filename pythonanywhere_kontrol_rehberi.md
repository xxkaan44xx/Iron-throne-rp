# ✅ PythonAnywhere Bot Kontrol Rehberi

## Task Eklendi - Şimdi Ne Yapmalı?

### 1. Task Durumunu Kontrol Et
- **Tasks** sayfasında task'ınız **"enabled"** durumunda olmalı
- Eğer **"disabled"** ise, **"Enable"** butonuna bas

### 2. Log Kontrol Et
- Task'ınızın yanında **"Show Log"** linki var
- Ona tıkla ve şu mesajları arayın:
```
✅ [Bot Name] PythonAnywhere'de çalışıyor!
📊 Bot X sunucuda aktif
```

### 3. Discord'da Test Et
Bot'unuza Discord'da şu komutları gönderin:
- `!test` - Bot durumunu test eder
- `!ping` - Gecikmeyi ölçer
- `!yardım` - Komutları listeler

### 4. Eğer Bot Cevap Vermiyorsa:

#### A) Token Kontrolü
**.bashrc** dosyasında token var mı?
```bash
export DISCORD_BOT_TOKEN="your_actual_token_here"
```

#### B) Dosya Yolu Kontrolü
Task command'ında kullanıcı adı doğru mu?
```
python3.10 /home/KULLANICIADIN/main.py
```

#### C) Task Yeniden Başlat
- Task'ı **"Disable"** yap
- Sonra **"Enable"** yap
- Ya da tamamen sil ve yeniden oluştur

### 5. Başarı Durumu:
✅ Task enabled
✅ Log'da "çalışıyor" mesajı
✅ Discord'da komutlara cevap veriyor
✅ Bot status: "🏰 GoT RP | PythonAnywhere 7/24"

Bu durumda bot 7/24 çalışıyor demektir!

### 6. Sorun Giderme:

**"Permission denied" hatası:**
- Dosya yolu yanlış olabilir
- Kullanıcı adını kontrol edin

**"No module named discord" hatası:**
- Console'da şu komutu çalıştırın:
```bash
pip3.10 install --user discord.py
```

**Token hatası:**
- .bashrc dosyasındaki token'ı kontrol edin
- Token'ın doğru olduğundan emin olun

Şu anda hangi aşamada sorun yaşıyorsunuz?