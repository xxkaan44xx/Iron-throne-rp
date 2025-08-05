

# Discord OAuth2 Kurulum Rehberi

## 1. Discord Developer Portal'da Uygulama Oluştur

1. **https://discord.com/developers/applications** adresine git
2. **"New Application"** butonuna tıkla
3. Uygulama adını gir: **"Iron Throne RP Dashboard"**
4. **"Create"** butonuna tıkla

## 2. OAuth2 Ayarları

1. Sol menüden **"OAuth2"** → **"General"** seç
2. **"Redirects"** bölümüne şu URL'yi ekle:
   ```
   https://[proje-adın].[kullanıcı-adın].replit.app/auth/discord/callback
   ```
   
   **Örnek:**
   ```
   https://iron-throne-rp.johndoe.replit.app/auth/discord/callback
   ```

3. **"Save Changes"** butonuna tıkla

## 3. Replit Secrets Ayarlama

Replit'te **Secrets** sekmesine git ve şunları ekle:

```
DISCORD_CLIENT_ID = [Discord uygulamanızın Client ID'si]
DISCORD_CLIENT_SECRET = [Discord uygulamanızın Client Secret'i]
```

### Client ID ve Secret Alma:

1. Discord Developer Portal'da uygulamanızı seç
2. **"OAuth2"** → **"General"** sayfasında:
   - **Client ID**: Sayfada görünen uzun numara
   - **Client Secret**: **"Reset Secret"** butonuna tıklayarak alabilirsiniz

**⚠️ ÖNEMLİ:** Client Secret'i bir kez gösterilir, kaydetmeyi unutmayın!

## 4. Admin Discord ID'leri Ayarlama

**premium_dashboard.py** dosyasında admin Discord ID'lerini ayarlayın:

```python
admin_discord_ids = [
    123456789012345678,  # İlk admin Discord ID
    987654321098765432,  # İkinci admin Discord ID
    # Daha fazla admin ID ekleyebilirsiniz
]
```

### Discord ID'nizi Öğrenmek:
1. Discord'da **Ayarlar** → **Gelişmiş** → **Geliştirici Modu**'nu açın
2. Profilinize sağ tıklayın → **"ID'yi Kopyala"**

## 5. Test Etme

1. Web sitenize git: `https://[proje-adın].replit.app`
2. **"Giriş"** butonuna tıkla
3. **"Discord ile Giriş Yap"** seç  
4. Discord'dan izin ver
5. Dashboard'a otomatik yönlendirileceksiniz

## 6. Admin Girişi Test Etme

1. `/admin` veya `/yonetim` sayfasına git
2. **"Discord ile Admin Girişi"** butonuna tıkla
3. Eğer Discord ID'niz admin listesindeyse admin paneline erişebilirsiniz

## 7. Manuel Giriş (Fallback)

Eğer OAuth2 çalışmazsa, Discord kullanıcı ID'nizi manuel olarak girebilirsiniz.

## Sorun Giderme

### "Discord OAuth2 yapılandırılmamış" Hatası:
- **DISCORD_CLIENT_ID** ve **DISCORD_CLIENT_SECRET** Secrets'ta doğru mu?
- Repl'i yeniden başlattınız mı?

### "Redirect URI Mismatch" Hatası:
- Discord Developer Portal'daki redirect URI ile gerçek URL'niz eşleşiyor mu?
- URL'nin sonunda `/auth/discord/callback` var mı?

### Admin Girişi Çalışmıyor:
- Discord ID'niz admin listesinde var mı?
- ID'yi doğru kopyaladınız mı?

---

**🎉 Artık Discord OAuth2 ile güvenli giriş yapabilirsiniz!**

