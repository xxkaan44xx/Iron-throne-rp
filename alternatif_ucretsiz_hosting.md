# 🌐 Cyclic.sh Alternatifi - Ücretsiz Sınırsız Hosting

## 1. **Render.com** ⭐ (En Kolay)
- **750 saat/ay ücretsiz** (günde 25 saat)
- Web dashboard kolay kullanım
- GitHub otomatik deployment

### Kurulum:
1. **render.com** → GitHub ile giriş
2. **"New Web Service"** 
3. Repository bağla
4. Environment variables ekle
5. Deploy et

## 2. **Railway.app** 
- **500 saat/ay ücretsiz**
- Modern web arayüzü
- Kolay deployment

### Kurulum:
1. **railway.app** → GitHub giriş
2. **"Deploy from GitHub repo"**
3. Bot repository seç
4. Environment variables
5. Deploy

## 3. **Fly.io**
- **Shared CPU ücretsiz**
- Command line tool
- Docker desteği

### Kurulum:
1. **fly.io** → Hesap oluştur
2. **flyctl** CLI tool indir
3. `fly deploy` komutu
4. Otomatik deployment

## 4. **PythonAnywhere** 
- **Always-on tasks ücretsiz**
- Python botlar için özel
- Web console

### Kurulum:
1. **pythonanywhere.com** → Free hesap
2. **Files** → Bot kodlarını yükle
3. **Tasks** → Always-on task oluştur
4. `python main.py` çalıştır

## 5. **Glitch.com**
- **Tamamen ücretsiz**
- Web editörü dahil
- Canlı kod değiştirme

### Kurulum:
1. **glitch.com** → GitHub import
2. Web editöründe kod düzenle
3. Environment variables ekle
4. Otomatik çalışır

## 6. **Heroku Alternatifi: Koyeb**
- **512MB RAM ücretsiz**
- Serverless platform
- Docker desteği

---

# 🚀 EN KOLAY: Render.com Kurulumu

## Adım 1: GitHub Hazırlama
GitHub'da repository oluştur ve bot kodunu yükle.

## Adım 2: Render.com'da Deployment
1. **render.com** → **"Sign Up"** → GitHub ile giriş
2. Dashboard'da **"New +"** → **"Web Service"**
3. **"Build and deploy from a Git repository"**
4. GitHub repository'nizi seç
5. Settings:
   ```
   Name: got-discord-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```

## Adım 3: Environment Variables
1. **"Environment"** sekmesi
2. **"Add Environment Variable"**
3. Key: `DISCORD_BOT_TOKEN`
4. Value: Discord bot token'ınız
5. **"Save Changes"**

## Adım 4: Deploy
- **"Create Web Service"** butonu
- Otomatik build başlar
- 5-10 dakika içinde aktif olur

---

# 📱 PythonAnywhere (En Basit)

## Avantajları:
- Tamamen ücretsiz
- Always-on tasks
- Python için optimize
- Web console

## Kurulum:
1. **pythonanywhere.com** → Free hesap
2. **Files** bölümünde bot dosyalarını oluştur
3. **Tasks** → **"Create scheduled task"**
4. Command: `python3.10 /home/yourusername/main.py`
5. **"Create"** butonu

---

# 🔧 Glitch.com (Canlı Editör)

## Avantajları:
- Web editörü dahil
- Canlı kod değiştirme
- Ücretsiz sınırsız
- Kolay paylaşım

## Kurulum:
1. **glitch.com** → **"New Project"**
2. **"Import from GitHub"**
3. Repository URL gir
4. **.env** dosyasında `DISCORD_BOT_TOKEN=your_token`
5. Otomatik çalışır

Hangi platformu denemek istiyorsuniz? Render.com en stabil seçenek.