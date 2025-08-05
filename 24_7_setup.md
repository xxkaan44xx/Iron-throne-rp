# 🏰 Game of Thrones Bot - 7/24 Çalışma Kılavuzu

## Replit'te Bot'u 7/24 Çalıştırma

Bot'unuzun kesintisiz çalışması için Replit'in **Reserved VM Deployment** özelliğini kullanmanız gerekiyor.

### Adım 1: Deployment Ayarları
1. Projenizin sağ üst köşesinde **"Deploy"** butonuna tıklayın
2. **"Reserved VM"** seçeneğini seçin 
3. Bu size garantili 7/24 çalışma sağlar

### Adım 2: Web Sunucusu (Mevcut)
✅ Flask web sunucusu zaten çalışıyor (Port 5000)
✅ UptimeRobot için `/health` endpoint'i hazır
✅ 24/7 ping sistemi aktif

### Adım 3: UptimeRobot Alternatifi
Reserved VM Deployment kullanırsanız UptimeRobot'a gerek yok, ama yine de kullanmak isterseniz:

**UptimeRobot URL'si:** `https://[proje-adı].[kullanıcı-adı].replit.app`

### Teknik Detaylar
- **Web Server**: Port 5000'de Flask çalışıyor
- **Bot Process**: Discord bot ana süreç
- **Health Check**: `/health` endpoint'i bot durumunu kontrol eder
- **Status Check**: `/status` endpoint'i sistem bilgilerini verir

### Neden UptimeRobot İşe Yaramadı?
- Free Replit projeler zamanaşımına uğrar
- Sadece Reserved VM sürekli çalışır
- Web ping tek başına yeterli değil

## Çözüm: Reserved VM Deployment! 🚀

Bot'unuz Reserved VM Deployment ile otomatik olarak 7/24 çalışacak.