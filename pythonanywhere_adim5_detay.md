# 📋 PythonAnywhere - 5. Adım Detaylı Rehber

## Always-On Task Oluşturma (Adım 5)

### Nerede?
1. PythonAnywhere dashboard'da **üst menüden "Tasks"** sekmesine tıkla
2. Sayfada **"Create scheduled task"** butonu var - ona bas

### Task Ayarları:
**Command** kutusuna şunu yaz:
```
python3.10 /home/KULLANICIADIN/main.py
```
**ÖNEMLİ:** `KULLANICIADIN` yerine kendi kullanıcı adınızı yazın!

**Örnek:**
- Kullanıcı adınız `mehmet123` ise:
```
python3.10 /home/mehmet123/main.py
```

### Zaman Ayarları:
- **Hour:** `*` (yıldız işareti)
- **Minute:** `*` (yıldız işareti) 
- **Day of month:** `*` (yıldız işareti)
- **Month:** `*` (yıldız işareti)
- **Day of week:** `*` (yıldız işareti)

Bu ayarlar "her zaman çalış" anlamına gelir.

### Son Adım:
**"Create"** butonuna bas.

## Alternatif: Always-On Task (Ücretsiz Hesapta)

Eğer "scheduled task" çalışmazsa:

1. **"Tasks"** sayfasında **"Always-On Tasks"** bölümüne bak
2. **"Create an always-on task"** butonu varsa ona bas
3. **Command:** `python3.10 /home/KULLANICIADIN/main.py`
4. **"Create"** bas

## Kontrolü:
- Task oluşturduktan sonra **"Tasks"** sayfasında görmelisiniz
- Status: **"enabled"** olmalı
- Bot Discord'da aktif hale gelecek

## Sorun Çözme:

### Task Görünmüyor?
- Refresh yapın (F5)
- **"Tasks"** sekmesini tekrar açın

### "Permission denied" hatası?
- Dosya yolunu kontrol edin: `/home/KULLANICIADIN/main.py`
- Kullanıcı adı doğru mu?

### Bot çalışmıyor?
1. **"Tasks"** → Task'ınızı bulun → **"Show Log"** 
2. Hata mesajlarını kontrol edin
3. Çoğunlukla token sorunu olur

## Token Kontrolü:
**.bashrc** dosyasında token var mı kontrol edin:
```bash
export DISCORD_BOT_TOKEN="your_token_here"
```

Hangi adımda takıldınız? Size daha detaylı yardım edebilirim.