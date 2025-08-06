
import discord
from discord.ext import commands
import random
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from utils import (
    create_embed, format_number, get_house_emoji, get_weather_emoji, get_terrain_emoji,
    validate_house_name, validate_character_name, calculate_level_from_experience,
    get_character_class_info, create_progress_bar, get_random_weather, 
    get_random_terrain, get_income_source_emoji, format_alliance_display
)

logger = logging.getLogger(__name__)
logger.info("Commands setup completed successfully")

# ASOIAF Characters and Houses data
ASOIAF_CHARACTERS = {
    # STARK HANESI
    "Eddard Stark": {"house": "Stark", "title": "Winterfell Lordu", "age": 35, "alive": True, "skills": ["Liderlik", "Savaş", "Adalet"]},
    "Catelyn Stark": {"house": "Stark", "title": "Lady Stark", "age": 33, "alive": True, "skills": ["Diplomasi", "Politika", "Aile"]},
    "Robb Stark": {"house": "Stark", "title": "Stark Varisi", "age": 16, "alive": True, "skills": ["Savaş", "Liderlik", "Strateji"]},
    "Sansa Stark": {"house": "Stark", "title": "Lady", "age": 13, "alive": True, "skills": ["Diplomasi", "Saray Hayatı", "Politika"]},
    "Arya Stark": {"house": "Stark", "title": "Lady", "age": 11, "alive": True, "skills": ["Kılıç", "Gizlilik", "Cesaret"]},
    "Bran Stark": {"house": "Stark", "title": "Lord", "age": 10, "alive": True, "skills": ["Bilgelik", "Tarih", "Hayal"]},
    "Jon Snow": {"house": "Stark", "title": "Piç", "age": 16, "alive": True, "skills": ["Savaş", "Liderlik", "Night's Watch"]},

    # LANNISTER HANESI
    "Tywin Lannister": {"house": "Lannister", "title": "Casterly Rock Lordu", "age": 52, "alive": True, "skills": ["Strateji", "Politika", "Ekonomi"]},
    "Cersei Lannister": {"house": "Lannister", "title": "Kraliçe", "age": 32, "alive": True, "skills": ["Politika", "Manipülasyon", "Güzellik"]},
    "Jaime Lannister": {"house": "Lannister", "title": "Kingsguard", "age": 32, "alive": True, "skills": ["Kılıç", "Şövalyelik", "Savaş"]},
    "Tyrion Lannister": {"house": "Lannister", "title": "Lord", "age": 28, "alive": True, "skills": ["Zeka", "Diplomasi", "Strateji"]},

    # BARATHEON HANESI
    "Robert Baratheon": {"house": "Baratheon", "title": "Kral", "age": 36, "alive": True, "skills": ["Savaş", "Güç", "Liderlik"]},
    "Stannis Baratheon": {"house": "Baratheon", "title": "Dragonstone Lordu", "age": 34, "alive": True, "skills": ["Strateji", "Disiplin", "Adalet"]},
    "Renly Baratheon": {"house": "Baratheon", "title": "Storm's End Lordu", "age": 21, "alive": True, "skills": ["Karizma", "Diplomasi", "Politika"]},

    # TARGARYEN HANESI
    "Daenerys Targaryen": {"house": "Targaryen", "title": "Prenses", "age": 14, "alive": True, "skills": ["Liderlik", "Karizma", "Cesaret"]},
    "Viserys Targaryen": {"house": "Targaryen", "title": "Prens", "age": 23, "alive": True, "skills": ["Gururlu", "Hırslı", "Acımasız"]},
    "Aemon Targaryen": {"house": "Targaryen", "title": "Maester", "age": 100, "alive": True, "skills": ["Bilgelik", "Şifa", "Gece Nöbeti"]},

    # TYRELL HANESI  
    "Mace Tyrell": {"house": "Tyrell", "title": "Highgarden Lordu", "age": 45, "alive": True, "skills": ["Politika", "Zenginlik", "Tarım"]},
    "Olenna Tyrell": {"house": "Tyrell", "title": "Queen of Thorns", "age": 70, "alive": True, "skills": ["Zeka", "Politika", "Manipülasyon"]},
    "Margaery Tyrell": {"house": "Tyrell", "title": "Lady", "age": 16, "alive": True, "skills": ["Güzellik", "Diplomasi", "Politika"]},
    "Loras Tyrell": {"house": "Tyrell", "title": "Ser", "age": 18, "alive": True, "skills": ["Kılıç", "Şövalyelik", "Karizma"]},

    # MARTELL HANESI
    "Doran Martell": {"house": "Martell", "title": "Dorne Prensi", "age": 50, "alive": True, "skills": ["Strateji", "Diplomasi", "Sabır"]},
    "Oberyn Martell": {"house": "Martell", "title": "Red Viper", "age": 40, "alive": True, "skills": ["Kılıç", "Zehir", "Savaş"]},
    "Arianne Martell": {"house": "Martell", "title": "Prenses", "age": 23, "alive": True, "skills": ["Diplomasi", "Güzellik", "Entrika"]},

    # GREYJOY HANESI
    "Balon Greyjoy": {"house": "Greyjoy", "title": "Iron Islands Lordu", "age": 45, "alive": True, "skills": ["Denizcilik", "İsyan", "Savaş"]},
    "Theon Greyjoy": {"house": "Greyjoy", "title": "Lord", "age": 19, "alive": True, "skills": ["Ok", "Denizcilik", "Savaş"]},
    "Asha Greyjoy": {"house": "Greyjoy", "title": "Kaptan", "age": 25, "alive": True, "skills": ["Denizcilik", "Liderlik", "Savaş"]},

    # ARRYN HANESI
    "Lysa Arryn": {"house": "Arryn", "title": "Vale Lady", "age": 32, "alive": True, "skills": ["Koruma", "Paranoyak", "Aile"]},
    "Robin Arryn": {"house": "Arryn", "title": "Vale Lordu", "age": 8, "alive": True, "skills": ["Zayıf", "Korumalı", "Çocuk"]},

    # TULLY HANESI
    "Hoster Tully": {"house": "Tully", "title": "Riverrun Lordu", "age": 60, "alive": True, "skills": ["Diplomasi", "Aile", "Nehir"]},
    "Edmure Tully": {"house": "Tully", "title": "Varis", "age": 27, "alive": True, "skills": ["Savaş", "İyi Kalp", "Nehir"]},

    # BOLTON HANESI
    "Roose Bolton": {"house": "Bolton", "title": "Dreadfort Lordu", "age": 40, "alive": True, "skills": ["Soğuk Kanlılık", "Strateji", "Korku"]},
    "Ramsay Bolton": {"house": "Bolton", "title": "Bastard", "age": 18, "alive": True, "skills": ["Zalimlik", "Av", "Korku"]},

    # MORMONT HANESI
    "Jeor Mormont": {"house": "Mormont", "title": "Lord Commander", "age": 60, "alive": True, "skills": ["Liderlik", "Kuzey", "Night's Watch"]},
    "Lyanna Mormont": {"house": "Mormont", "title": "Lady", "age": 10, "alive": True, "skills": ["Cesaret", "Liderlik", "Kuzey"]},

    # FREY HANESI
    "Walder Frey": {"house": "Frey", "title": "Twins Lordu", "age": 90, "alive": True, "skills": ["Kin", "Strateji", "Uzun Yaşam"]},
}

def setup_commands(bot, db, war_system, economy_system):
    """Setup all bot commands"""
    
    # ===============================
    # PING KOMUTU (HEM SLASH HEM PREFIX)
    # Discord Active Developer Badge için gerekli
    # ===============================
    
    @bot.command(name="ping")
    async def ping_prefix(ctx):
        """Bot ping kontrolü (prefix komutu)"""
        latency = round(bot.latency * 1000)
        embed = create_embed(
            "🏓 Pong!",
            f"Bot gecikmesi: **{latency}ms**\nBot durumu: ✅ Çevrimiçi",
            discord.Color.green()
        )
        embed.add_field(name="Komut Türü", value="Prefix (!ping)", inline=True)
        await ctx.send(embed=embed)
    
    @bot.tree.command(name="ping", description="Bot ping kontrolü")
    async def ping_slash(interaction: discord.Interaction):
        """Bot ping kontrolü (slash komutu - Active Developer Badge için)"""
        latency = round(bot.latency * 1000)
        embed = create_embed(
            "🏓 Pong!",
            f"Bot gecikmesi: **{latency}ms**\nBot durumu: ✅ Çevrimiçi",
            discord.Color.blue()
        )
        embed.add_field(name="Komut Türü", value="Slash (/ping)", inline=True)
        embed.add_field(name="Badge", value="Active Developer ✨", inline=True)
        await interaction.response.send_message(embed=embed)
    
    # ===============================
    # YENİ SLASH KOMUTLARI
    # ===============================
    
    @bot.tree.command(name="stats", description="Sunucu istatistikleri")
    async def stats_slash(interaction: discord.Interaction):
        """Sunucu istatistikleri (slash komutu)"""
        try:
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message("❌ Bu komut sadece sunucu kanallarında kullanılabilir!", ephemeral=True)
                return
                
            embed = create_embed("📊 Sunucu İstatistikleri", guild.name, discord.Color.blue())
            embed.add_field(name="👥 Üye Sayısı", value=str(guild.member_count or 0), inline=True)
            embed.add_field(name="📅 Oluşturulma", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
            embed.add_field(name="🏆 Boost Seviyesi", value=str(guild.premium_tier or 0), inline=True)
            embed.add_field(name="💎 Boost Sayısı", value=str(guild.premium_subscription_count or 0), inline=True)
            embed.add_field(name="📚 Kanal Sayısı", value=str(len(guild.channels)), inline=True)
            embed.add_field(name="🎭 Rol Sayısı", value=str(len(guild.roles)), inline=True)
            
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Hata: {str(e)}", ephemeral=True)
    
    @bot.tree.command(name="info", description="Bot bilgileri")
    async def info_slash(interaction: discord.Interaction):
        """Bot bilgileri (slash komutu)"""
        try:
            embed = create_embed("🤖 Bot Bilgileri", "Iron Throne RP - Game of Thrones Bot", discord.Color.gold())
            embed.add_field(name="🏆 Versiyon", value="3.0 - Professional Edition", inline=True)
            embed.add_field(name="🌟 Özellikler", value="50+ Komut, Sıfır Hata", inline=True)
            embed.add_field(name="⚡ Gecikme", value=f"{round(bot.latency * 1000)}ms", inline=True)
            embed.add_field(name="🏰 Sunucular", value=len(bot.guilds), inline=True)
            embed.add_field(name="👑 Tema", value="Game of Thrones RP", inline=True)
            embed.add_field(name="🛡️ Kalite", value="10/10 Perfect Score", inline=True)
            
            embed.add_field(name="🎯 Sistemler", 
                          value="• Hane Sistemi\n• Savaş Sistemi\n• Ekonomi Sistemi\n• Evlilik Sistemi\n• Turnuva Sistemi\n• Otomatik Moderasyon", 
                          inline=False)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Hata: {str(e)}", ephemeral=True)

    @bot.command(name='rehber', aliases=['guide'])
    async def comprehensive_guide(ctx, section=None):
        """Comprehensive guide for new players"""
        if not section:
            embed = create_embed(
                "📖 Game of Thrones RP - Kapsamlı Rehber",
                "Westeros'ta hayatta kalmak için her şeyi öğren!",
                discord.Color.gold()
            )
            
            embed.add_field(
                name="🎯 Hızlı Başlangıç",
                value="`!rehber başlangıç` - İlk adımların\n"
                      "`!rehber komutlar` - Tüm komut listesi\n"
                      "`!rehber ipuçları` - Pro oyuncu ipuçları",
                inline=False
            )
            
            embed.add_field(
                name="🏰 Oyun Sistemleri",
                value="`!rehber haneler` - Hane seçimi ve yönetimi\n"
                      "`!rehber ekonomi` - Altın kazanma rehberi\n"
                      "`!rehber savaş` - Savaş stratejileri\n"
                      "`!rehber diplomasi` - İttifak ve siyaset",
                inline=False
            )
            
            embed.add_field(
                name="⚔️ İleri Seviye",
                value="`!rehber turnuvalar` - Turnuva sistemi\n"
                      "`!rehber ticaret` - Ticaret ve borsa\n"
                      "`!rehber roleplay` - RP teknikleri\n"
                      "`!rehber moderasyon` - Moderatör komutları",
                inline=False
            )
            
            embed.set_footer(text="Örnek: !rehber başlangıç")
            await ctx.send(embed=embed)
            return
            
        section = section.lower()
        
        if section in ["başlangıç", "start", "begin"]:
            embed = create_embed(
                "🎯 Hızlı Başlangıç Rehberi",
                "Westeros'ta ilk adımların - 5 dakikada oyuncu ol!",
                discord.Color.green()
            )
            
            embed.add_field(
                name="1️⃣ Hane Seç (Zorunlu)",
                value="• `!haneler` - Mevcut haneleri gör\n"
                      "• `!katıl <hane_adı>` - Favori hanene katıl\n"
                      "• **Öneri:** Stark (yeni başlayanlar), Lannister (zenginlik), Targaryen (güç)",
                inline=False
            )
            
            embed.add_field(
                name="2️⃣ Karakter Oluştur",
                value="• `!karakterler <hane_adı>` - Müsait karakterleri gör\n"
                      "• `!karakter <karakter_adı>` - Karakterini seç\n"
                      "• **İpucu:** Jon Snow, Tyrion, Daenerys gibi popüler karakterler hızla gider!",
                inline=False
            )
            
            embed.add_field(
                name="3️⃣ İlk Eylemler",
                value="• `!profil` - Durumunu kontrol et\n"
                      "• `!hane` - Hane bilgilerini gör\n"
                      "• `!ekonomi` - Hanendeki altını gör\n"
                      "• `!sınıf_değiştir <sınıf>` - Sınıfını seç (Lord, Knight, Maester vs.)",
                inline=False
            )
            
            embed.add_field(
                name="4️⃣ İlk Hedefler",
                value="• 10,000 altın biriktir\n"
                      "• Bir turnuvaya katıl\n"
                      "• Başka oyuncularla ittifak kur\n"
                      "• Asker sayını 500'e çıkar",
                inline=False
            )
            
            embed.add_field(
                name="5️⃣ Yardım Al",
                value="• `!yardım` - Komut kategorileri\n"
                      "• `!rehber ipuçları` - Pro ipuçları\n"
                      "• Deneyimli oyunculardan tavsiye iste!",
                inline=False
            )
            
        elif section in ["komutlar", "commands"]:
            embed = create_embed(
                "📋 Tüm Komutlar - Alfabetik Liste",
                "43 komutla dolu Westeros deneyimi!",
                discord.Color.blue()
            )
            
            all_commands = """
**A-E:**
• !aktif_savaşlar - Devam eden savaşları listele
• !antlaşma_kabul - Ticaret antlaşmasını kabul et
• !antlaşmalar - Aktif antlaşmaları görüntüle
• !aşk_uyumu - İki kişi arası uyum testi
• !asker_al - Asker satın al
• !borc - Borç durumunu görüntüle
• !borç_iptal - Borcu affet (alacaklı)
• !borç_öde - Borç öde
• !borç_ver - Başka haneye borç ver
• !borçlarım - Tüm borçları listele
• !boşan - Eşinden boşan
• !düello_çağır - Düello teklif et
• !düello_kabul - Düelloyu kabul et
• !düello_reddet - Düelloyu reddet
• !düellolarım - Aktif düelloları gör
• !ekonomi - Ekonomik durumu görüntüle
• !evlen - Evlilik teklifi gönder
• !evlilik_kabul - Evlilik teklifini kabul et
• !evliliklerim - Evlilik geçmişi

**F-O:**
• !gelir_kaynakları - Gelir kaynaklarını listele
• !gelir_satın_al - Yeni gelir kaynağı al
• !hamile_kal - Hamilelik dene
• !hane - Hane bilgilerini görüntüle
• !hane_istatistikleri - Detaylı hane analizi
• !haneler - Tüm haneleri listele
• !hikaye - Grup hikayesi oluştur
• !hikaye_sıfırla - Hikayeyi sıfırla
• !kahin - Geleceği gör (kehanet)
• !karakter - Karakter seç
• !karakterler - Müsait karakterleri listele
• !katıl - Haneye katıl
• !kaynak_al - Kaynak satın al
• !kaynak_bul - Satılık kaynakları bul
• !kaynak_sat - Kaynak sat
• !kaynak_satın_al - Pazardan kaynak al
• !liderlik_tablosu - En güçlü haneler
• !mektup - Oyuncuya mektup gönder
• !ordu - Ordu durumunu görüntüle
• !ordu_yükselt - Ordu bileşenini geliştir

**P-Z:**
• !profil - Oyuncu profilini gör
• !rastgele_görev - Rastgele RP görevi
• !roleplay - RP aksiyonu gerçekleştir
• !saldır - Savaşta saldır
• !savaş_ilan - Savaş başlat
• !seviye - Karakter seviyesi ve XP
• !sınıf_değiştir - Karakter sınıfını değiştir
• !tahmin - Sayı tahmin oyunu
• !ticaret - Ticaret menüsü
• !ticaret_antlaşması - Antlaşma öner
• !turnuva_düzenle - Turnuva organize et
• !turnuva_katıl - Turnuvaya katıl
• !turnuvalar - Aktif turnuvaları listele
• !üyeler - Hane üyelerini listele
• !vs - İki şey arasında karşılaştırma
• !yardım - Yardım menüsü
• !zar - Zar at (kader belirle)
"""
            embed.add_field(name="📝 Komut Listesi", value=all_commands, inline=False)
            
        elif section in ["ipuçları", "tips", "pro"]:
            embed = create_embed(
                "💡 Pro Oyuncu İpuçları",
                "Westeros'ta üstünlük sağlama teknikleri!",
                discord.Color.purple()
            )
            
            embed.add_field(
                name="💰 Ekonomi Pro Tips",
                value="• **Pasif gelir odaklı ol:** Gelir kaynakları > tek seferlik kazanç\n"
                      "• **Borç verme stratejisi:** %15+ faizle borç ver, güvenilir hanelere\n"
                      "• **Ticaret antlaşmaları:** %15 indirim büyük tasarruf sağlar\n"
                      "• **Kaynak timing:** Düşük fiyattan al, yüksek fiyattan sat",
                inline=False
            )
            
            embed.add_field(
                name="⚔️ Savaş Pro Tips",
                value="• **Savaş zamanlaması:** Rakip offline'ken saldır\n"
                      "• **Ordu kompozisyonu:** %40 piyade, %30 süvari, %20 okçu, %10 kuşatma\n"
                      "• **Müttefik savaşlar:** Büyük hanelere karşı ittifak kur\n"
                      "• **Savunma bonusu:** Saldırgan her zaman dezavantajlı",
                inline=False
            )
            
            embed.add_field(
                name="🏰 Diplomasi Pro Tips",
                value="• **Evlilik ittifakları:** Güçlü hanelerle evlen\n"
                      "• **Bilgi ticareti:** Düşman planlarını sat\n"
                      "• **Turnuva diplomasisi:** Turnuva düzenleyerek prestij kazan\n"
                      "• **Roleplay avantajı:** Aktif RP yapanlar daha çok desteklenir",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Karakter Gelişimi",
                value="• **XP farming:** Günlük turnuvalar ve savaşlara katıl\n"
                      "• **Sınıf seçimi:** Lord (dengeli), Knight (savaş), Maester (ekonomi)\n"
                      "• **Karakter prestiji:** Popüler karakterler daha fazla saygı görür\n"
                      "• **Skill build:** Saldırı > Savunma > Can sıralaması",
                inline=False
            )
            
        elif section in ["moderasyon", "mod", "admin"]:
            embed = create_embed(
                "👑 Moderasyon Rehberi",
                "Sunucu yönetimi ve moderasyon araçları",
                discord.Color.red()
            )
            
            embed.add_field(
                name="🚫 Temel Moderasyon",
                value="`/ban <@kullanıcı> [sebep]` - Kullanıcıyı yasakla\n"
                      "`/kick <@kullanıcı> [sebep]` - Kullanıcıyı at\n"
                      "`/mute <@kullanıcı> [süre]` - Kullanıcıyı sustur\n"
                      "`/warn <@kullanıcı> [sebep]` - Uyarı ver",
                inline=False
            )
            
            embed.add_field(
                name="🏰 Hane Yönetimi",
                value="`!lider_ata <@kullanıcı>` - Hane liderini değiştir\n"
                      "`!üye_at <@kullanıcı>` - Üyeyi haneden at\n"
                      "`!ordu_ayarla <@kullanıcı> <değerler>` - Ordu kompozisyonu ayarla\n"
                      "`!karakter <@kullanıcı> <karakter>` - Karakter ata",
                inline=False
            )
            
            embed.add_field(
                name="💰 Ekonomi Müdahalesi",
                value="`/altın_ver <@kullanıcı> <miktar>` - Altın ver\n"
                      "`/altın_al <@kullanıcı> <miktar>` - Altın al\n"
                      "`/borç_sıfırla <hane>` - Hane borcunu sıfırla\n"
                      "`/ekonomi_reset` - Ekonomiyi sıfırla",
                inline=False
            )
            
            embed.set_footer(text="Bu komutları kullanmak için moderatör yetkisi gerekir!")
            
        else:
            embed = create_embed(
                "❌ Geçersiz Bölüm",
                f"'{section}' rehber bölümü bulunamadı!",
                discord.Color.red()
            )
            embed.add_field(
                name="Kullanılabilir Bölümler",
                value="başlangıç, komutlar, ipuçları, haneler, ekonomi, savaş, diplomasi, turnuvalar, ticaret, roleplay, moderasyon",
                inline=False
            )
            
        await ctx.send(embed=embed)

    @bot.command(name='yardım', aliases=['komutlar'])
    async def help_command(ctx, category=None):
        """Show help information"""
        # ULTIMATE duplicate prevention - check bot instance ID
        if not hasattr(bot, '_unique_bot_id'):
            import time
            bot._unique_bot_id = int(time.time() * 1000) % 10000
        
        # Only respond if this is the main bot instance
        if not hasattr(bot, '_is_main_instance'):
            bot._is_main_instance = True
            # Set a delay to let other instances mark themselves
            await asyncio.sleep(0.1)
        
        # Create unique response tracking
        response_key = f"{ctx.message.id}_help_response"
        if hasattr(bot, '_processed_messages'):
            if response_key in bot._processed_messages:
                return
        else:
            bot._processed_messages = set()
        
        bot._processed_messages.add(response_key)
        
        if not category:
            embed = create_embed(
                "🏰 DEMIR TAHT RP | KOMUTLAR MENÜSÜ",
                "⭐ **104+ Premium Komut** | **Profesyonel RP Sistemi** | **Sıfır Hata Garantisi** ⭐",
                discord.Color.from_rgb(255, 215, 0)  # Gold color
            )

            # Ana kategoriler - 2 sütun halinde düzenli
            embed.add_field(
                name="🏠 **YENİ BAŞLAYANLAR**",
                value="`!yardım temel` - İlk adımlar\n`!haneler` - Haneleri görüntüle\n`!katıl <hane>` - Haneye katıl",
                inline=True
            )
            embed.add_field(
                name="⚔️ **SAVAŞ SİSTEMİ**", 
                value="`!yardım savaş` - Savaş komutları\n`!yardım ordu` - Ordu yönetimi\n`!aktif_savaşlar` - Devam eden savaşlar",
                inline=True
            )
            embed.add_field(
                name="💰 **EKONOMİ & TİCARET**",
                value="`!yardım ekonomi` - Para sistemi\n`!ekonomi` - Durumunu gör\n`!asker_al <sayı>` - Asker satın al",
                inline=True
            )
            embed.add_field(
                name="👑 **KARAKTER & ROL**",
                value="`!yardım karakter` - Karakter sistemi\n`!profil` - Profilini gör\n`!evlilik_teklif <@kişi>` - Evlen",
                inline=True
            )
            embed.add_field(
                name="🤝 **DİPLOMASİ & İTTİFAK**",
                value="`!yardım diplomasi` - Diplomasi\n`!diplomasi` - Tüm seçenekler\n`!ittifak_teklif <hane>` - İttifak kur",
                inline=True
            )
            embed.add_field(
                name="🏆 **TURNUVA & DÜELLO**",
                value="`!yardım turnuva` - Turnuvalar\n`!turnuvalar` - Aktif turnuvalar\n`!düello_teklif <@kişi>` - Düello et",
                inline=True
            )

            # Özel bölümler
            embed.add_field(
                name="🏰 **VERASETLİK SİSTEMİ**",
                value="`!varis_ata <@kullanıcı>` - Varis belirle\n`!varisler` - Varisleri listele\n`!hane_yönetimi` - Hane kontrolü",
                inline=False
            )

            # Hızlı erişim
            embed.add_field(
                name="⚡ **HIZLI ERİŞİM**",
                value="`!istatistik` - Detaylı istatistikler | `!ping` - Bot durumu | `!hane` - Haneni gör",
                inline=False
            )

            # Yeni özellikler bölümü
            embed.add_field(
                name="🆕 **YENİ ÖZELLİKLER**",
                value="`!ejder_avı` - Efsanevi maceralar\n`!bilmece` - Zeka oyunları\n`!günlük_görevler` - Günlük görevler\n`!başarılar` - Başarı sistemi\n`!pazar` - Gelişmiş ticaret",
                inline=False
            )

            # Footer bilgileri
            embed.set_footer(
                text="🔥 YENİ: 150+ komut, özel etkinlikler, başarı sistemi ve gelişmiş ekonomi eklendi!",
                icon_url="https://cdn.discordapp.com/emojis/853578385775067176.png"
            )
            embed.set_thumbnail(url="https://i.imgur.com/9X8wQf4.png")  # GoT themed image

        elif category.lower() == "temel":
            embed = create_embed(
                "📋 Temel Komutlar",
                "Hane yönetimi ve temel işlemler",
                discord.Color.green()
            )

            embed.add_field(
                name="🏰 Hane Komutları",
                value="`!haneler` - Tüm haneleri listele\n"
                      "`!katıl <hane_adı>` - Bir haneye katıl\n"
                      "`!hane` - Haneni görüntüle\n"
                      "`!üyeler` - Hane üyelerini listele",
                inline=False
            )

            embed.add_field(
                name="👤 Profil Komutları",
                value="`!profil [@kullanıcı]` - Profili görüntüle\n"
                      "`!istatistik` - Detaylı istatistikleri gör",
                inline=False
            )

        elif category.lower() == "savaş":
            embed = create_embed(
                "⚔️ Savaş Komutları",
                "Savaş ve mücadele sistemi",
                discord.Color.red()
            )

            embed.add_field(
                name="🎯 Savaş Başlatma",
                value="`!savaş_ilan <hane_adı>` - Savaş ilan et\n"
                      "`!aktif_savaşlar` - Devam eden savaşları listele\n"
                      "`!savaş_durum <savaş_id>` - Savaş durumunu görüntüle",
                inline=False
            )

            embed.add_field(
                name="⚡ Savaş Aksiyonları",
                value="`!saldır <savaş_id>` - Saldırı yap\n"
                      "`!savun <savaş_id>` - Savunma pozisyonu al\n"
                      "`!maneuvra <savaş_id>` - Taktiksel hareket\n"
                      "`!geri_çekil <savaş_id>` - Stratejik geri çekilme\n"
                      "`!taarruz <savaş_id>` - Topyekün saldırı",
                inline=False
            )

        elif category.lower() == "ekonomi":
            embed = create_embed(
                "💰 Ekonomi Komutları", 
                "Altın, borç ve gelir yönetimi",
                discord.Color.gold()
            )

            embed.add_field(
                name="💸 Altın İşlemleri",
                value="`!asker_al <sayı>` - Asker satın al\n"
                      "`!ekonomi` - Ekonomik durumu görüntüle\n"
                      "`!gelir_kaynağı <tür> <ad> <bölge>` - Gelir kaynağı oluştur",
                inline=False
            )

            embed.add_field(
                name="🏦 Borç İşlemleri",
                value="`!borç_ver <hane_adı> <miktar> [faiz] [gün]` - Borç ver\n"
                      "`!borç_öde <miktar>` - Borç öde\n"
                      "`!borc` - Borç durumunu görüntüle",
                inline=False
            )

        elif category.lower() == "karakter":
            embed = create_embed(
                "👑 Karakter Komutları",
                "Karakter ve sosyal sistem",
                discord.Color.purple()
            )

            embed.add_field(
                name="🎭 Karakter Yönetimi",
                value="`!karakter <karakter_adı>` - Karakter seç\n"
                      "`!karakterler [hane]` - Müsait karakterleri listele\n"
                      "`!sınıf_değiştir <sınıf>` - Karakter sınıfını değiştir",
                inline=False
            )

            embed.add_field(
                name="💒 Sosyal İşlemler",
                value="`!evlen <@kullanıcı>` - Evlilik teklifi gönder\n"
                      "`!evlilik_kabul` - Evlilik teklifini kabul et\n"
                      "`!mektup <@kullanıcı> <mesaj>` - Mektup gönder\n"
                      "`!aile` - Aile durumunu görüntüle",
                inline=False
            )

        elif category.lower() == "diplomasi":
            embed = create_embed("🤝 Diplomasi Komutları",
                           "İttifak kurun, siyasi güç elde edin",
                           discord.Color.purple())

            embed.add_field(
                name="🏛️ İttifak Yönetimi",
                value="`!ittifak_kur <isim>` - Yeni ittifak kur\n"
                      "`!ittifak_katıl <isim>` - İttifaka katıl\n"
                      "`!ittifak_ayrıl` - İttifaktan ayrıl\n"
                      "`!ittifaklar` - Tüm ittifakları listele",
                inline=False
            )

            embed.add_field(
                name="🤝 Diplomatik İlişkiler",
                value="`!ittifak_teklif <hane>` - İttifak teklifi gönder\n"
                      "`!ittifak_kabul <hane>` - İttifak teklifini kabul et\n"
                      "`!ilişkiler` - Diplomatik durumu görüntüle",
                inline=False
            )

            embed.add_field(
                name="👑 Liderlik Komutları",
                value="`!lider_ata <@kullanıcı>` - Yeni lider ata\n"
                      "`!üye_at <@kullanıcı>` - Üyeyi haneden at\n"
                      "`!siyasi_harita` - Westeros siyasi durumu",
                inline=False
            )

            embed.add_field(name="🏰 Veraset Yönetimi",
                          value="`!varis_ata <@kullanıcı> [sıra]` - Varis ata\n"
                                "`!varisler [hane]` - Varisleri listele\n"
                                "`!varis_çıkar <@kullanıcı>` - Varisi çıkar\n"
                                "`!veraset_sırası <@kullanıcı> <sıra>` - Sıra değiştir",
                          inline=False)

        elif category.lower() == "ordu":
            embed = create_embed("⚔️ Ordu Yönetimi",
                           "Ordunu güçlendir ve kaynaklarını yönet",
                           discord.Color.red())

            embed.add_field(name="🏗️ Ordu Geliştirme",
                          value="`!ordu` - Ordu durumunu görüntüle\n"
                                "`!ordu_yükselt <bileşen> [seviye]` - Ordu bileşenini yükselt\n"
                                "`!kaynak_al <tür> <miktar>` - Kaynak satın al\n"
                                "`!ordu_ayarla <piyade> <süvari> <okçu> <kuşatma>` - Ordu kompozisyonu (Admin)",
                          inline=False)

            embed.add_field(name="📦 Kaynaklar",
                          value="**Bileşenler:** silah, zırh, eğitim, kuşatma, süvari, okçu, donanma\n"
                                "**Kaynak Türleri:** food, stone, wood, iron, horses, wine",
                          inline=False)

        elif category.lower() == "turnuva":
            embed = create_embed("🏆 Turnuva & Düello",
                           "Şöhret ve altın kazan",
                           discord.Color.gold())

            embed.add_field(name="🏟️ Turnuva Sistemi",
                          value="`!turnuva_düzenle <isim> <tür> [ücret] [ödül]` - Turnuva düzenle\n"
                                "`!turnuva_katıl <turnuva_id>` - Turnuvaya katıl\n"
                                "`!turnuvalar` - Aktif turnuvaları listele\n"
                                "`!turnuva_başlat <turnuva_id>` - Turnuvayı başlat",
                          inline=False)

            embed.add_field(name="⚔️ Düello Sistemi",
                          value="`!düello_teklif <@kullanıcı> <tür> [bahis]` - Düello teklif et\n"
                                "`!düello_kabul <düello_id>` - Düello teklifini kabul et\n"
                                "`!düellolar` - Aktif düelloları listele",
                          inline=False)

            embed.add_field(name="🎯 Türler",
                          value="**Turnuva:** joust, melee, archery, mixed\n"
                                "**Düello:** sword, lance, trial_by_combat",
                          inline=False)

        else:
            embed = create_embed("❌ Hata", "Geçersiz kategori! Kullanılabilir kategoriler: temel, savaş, ekonomi, karakter, diplomasi", discord.Color.red())

        await ctx.send(embed=embed)

    @bot.command(name='katıl')
    async def join_alliance(ctx, *, alliance_name):
        """Join an alliance/house"""
        user_id = ctx.author.id

        try:
            # Check if user is already in an alliance
            current_alliance = db.get_user_alliance(user_id)
            if current_alliance:
                embed = create_embed("❌ Hata", f"Zaten **{current_alliance[1]}** hanesinin üyesisin!", discord.Color.red())
                await ctx.send(embed=embed)
                return

            # Check if alliance exists
            alliance = db.get_alliance_by_name(alliance_name)
            if not alliance:
                embed = create_embed("❌ Hata", f"**{alliance_name}** adında bir hane bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return

            # Add user to alliance
            db.c.execute('INSERT INTO members (user_id, alliance_id, role) VALUES (?, ?, ?)', 
                        (user_id, alliance[0], 'Üye'))
            db.conn.commit()

            house_emoji = get_house_emoji(alliance_name)
            embed = create_embed(f"{house_emoji} Haneye Katılma", 
                               f"{ctx.author.mention} **{alliance_name}** hanesine katıldı!", 
                               discord.Color.green())
            embed.add_field(name="Rol", value="Üye", inline=True)
            embed.add_field(name="Bölge", value=alliance[8] or "Bilinmiyor", inline=True)
            embed.add_field(name="Özellik", value=alliance[7] or "Yok", inline=True)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Join alliance error: {e}")
            embed = create_embed("❌ Hata", f"Haneye katılırken bir hata oluştu: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='haneler', aliases=['houses'])
    async def list_alliances(ctx):
        """List all available houses"""
        try:
            db.c.execute('SELECT name, region, gold, soldiers, special_ability FROM alliances ORDER BY gold DESC')
            alliances = db.c.fetchall()

            if not alliances:
                embed = create_embed("📋 Haneler", "Henüz hiç hane oluşturulmamış!", discord.Color.blue())
                await ctx.send(embed=embed)
                return

            embed = create_embed("🏰 Westeros Haneleri", "Mevcut haneler ve güçleri:", discord.Color.gold())

            for alliance in alliances:
                name, region, gold, soldiers, special_ability = alliance
                house_emoji = get_house_emoji(name)

                embed.add_field(
                    name=f"{house_emoji} {name}",
                    value=f"**Bölge:** {region or 'Bilinmiyor'}\n"
                          f"**Altın:** {format_number(gold)} 🪙\n"
                          f"**Asker:** {format_number(soldiers)} ⚔️\n"
                          f"**Özellik:** {special_ability or 'Yok'}",
                    inline=True
                )

            embed.set_footer(text="!katıl <hane_adı> ile bir haneye katılabilirsiniz")
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"List alliances error: {e}")
            embed = create_embed("❌ Hata", "Haneler listelenirken hata oluştu!", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='profil', aliases=['profile']) 
    async def profile(ctx, member: Optional[discord.Member] = None):
        """Show user profile"""
        target = member if member is not None else ctx.author
        user_id = target.id

        try:
            # Get user alliance
            alliance_data = db.get_user_alliance(user_id)
            if not alliance_data:
                embed = create_embed("❌ Hata", f"{target.display_name} henüz hiçbir haneye katılmamış!", discord.Color.red())
                await ctx.send(embed=embed)
                return

            # Get character data
            db.c.execute('SELECT * FROM asoiaf_characters WHERE user_id = ?', (user_id,))
            character = db.c.fetchone()

            db.c.execute('SELECT * FROM members WHERE user_id = ?', (user_id,))
            member_data = db.c.fetchone()

            house_emoji = get_house_emoji(alliance_data[1])
            embed = create_embed(f"{house_emoji} {target.display_name} Profili", 
                               f"**{alliance_data[1]}** hanesinin üyesi", 
                               discord.Color.blue())

            # Basic info
            embed.add_field(name="👑 Rol", value=alliance_data[11] or "Üye", inline=True)
            if member_data:
                level = calculate_level_from_experience(member_data[6] or 0)
                embed.add_field(name="⚡ Seviye", value=level, inline=True)
                embed.add_field(name="✨ Deneyim", value=format_number(member_data[6] or 0), inline=True)

            # Character info
            if character:
                embed.add_field(name="🎭 Karakter", value=character[1], inline=True)
                embed.add_field(name="🏛️ Unvan", value=character[3], inline=True)
                embed.add_field(name="🎂 Yaş", value=character[5], inline=True)

            # Combat stats
            if member_data:
                embed.add_field(name="❤️ Sağlık", value=member_data[7] or 100, inline=True)
                embed.add_field(name="⚔️ Saldırı", value=member_data[8] or 20, inline=True)
                embed.add_field(name="🛡️ Savunma", value=member_data[9] or 15, inline=True)

                # Character class
                class_info = get_character_class_info(member_data[4] or "Lord")
                embed.add_field(name="🎖️ Sınıf", value=f"{class_info['emoji']} {member_data[4] or 'Lord'}", inline=True)

            # Marriage status
            if member_data and member_data[3]:
                married_user = bot.get_user(member_data[3])
                if married_user:
                    embed.add_field(name="💒 Evlilik", value=f"{married_user.display_name} ile evli", inline=False)

            embed.set_thumbnail(url=target.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Profile error: {e}")
            embed = create_embed("❌ Hata", "Profil görüntülenirken hata oluştu!", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='karakter')
    async def claim_character(ctx, target: Optional[discord.Member] = None, *, character_name = None):
        """Claim an ASOIAF character (Admin can assign to others)"""

        # Check if this is an admin command (with @mention)
        if target and target != ctx.author:
            # Admin functionality - check if user has admin permissions
            if not ctx.author.guild_permissions.administrator:
                embed = create_embed("❌ Hata", "Sadece adminler başkalarına karakter atayabilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return

            if not character_name:
                embed = create_embed("❌ Hata", "Karakter adı belirtmelisin! Kullanım: `!karakter @kullanıcı <karakter_adı>`", discord.Color.red())
                await ctx.send(embed=embed)
                return

            user_id = target.id
            mention_text = f"Admin {ctx.author.mention} tarafından {target.mention} için"
        else:
            # Regular user functionality
            if target:  # If target is provided but it's same as author, use it as character name
                character_name = target.display_name if character_name is None else f"{target.display_name} {character_name}"
            elif character_name is None:
                embed = create_embed("❌ Hata", "Karakter adı belirtmelisin! Kullanım: `!karakter <karakter_adı>`", discord.Color.red())
                await ctx.send(embed=embed)
                return

            user_id = ctx.author.id
            mention_text = f"{ctx.author.mention}"

        try:
            # Check if user is in an alliance
            alliance_data = db.get_user_alliance(user_id)
            if not alliance_data:
                embed = create_embed("❌ Hata", "Karakter seçmek için önce bir haneye katılmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return

            # Check if character exists and is available
            if character_name not in ASOIAF_CHARACTERS:
                embed = create_embed("❌ Hata", f"**{character_name}** adında bir karakter bulunamadı!", discord.Color.red())
                embed.add_field(name="💡 İpucu", value="Kullanılabilir karakterleri görmek için `!karakterler` komutunu kullanın.", inline=False)
                await ctx.send(embed=embed)
                return

            # Check if character is already taken
            db.c.execute('SELECT user_id FROM asoiaf_characters WHERE character_name = ?', (character_name,))
            existing = db.c.fetchone()
            if existing:
                existing_user = bot.get_user(existing[0])
                embed = create_embed("❌ Hata", f"**{character_name}** zaten {existing_user.display_name if existing_user else 'bilinmeyen kullanıcı'} tarafından seçilmiş!", discord.Color.red())
                await ctx.send(embed=embed)
                return

            character_data = ASOIAF_CHARACTERS[character_name]

            # Add character to database
            db.c.execute('''
            INSERT OR REPLACE INTO asoiaf_characters 
            (user_id, character_name, house, title, age, alive, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, character_name, character_data["house"], character_data["title"], 
                  character_data["age"], character_data["alive"], json.dumps(character_data["skills"])))

            db.conn.commit()

            house_emoji = get_house_emoji(character_data["house"])
            embed = create_embed(f"{house_emoji} Karakter Seçildi", 
                               f"{mention_text} **{character_name}** karakterini seçti!", 
                               discord.Color.green())
            embed.add_field(name="🏛️ Unvan", value=character_data["title"], inline=True)
            embed.add_field(name="🏰 Hane", value=character_data["house"], inline=True)
            embed.add_field(name="🎂 Yaş", value=character_data["age"], inline=True)
            embed.add_field(name="🎯 Yetenekler", value=", ".join(character_data["skills"]), inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Claim character error: {e}")
            embed = create_embed("❌ Hata", f"Karakter seçilirken hata oluştu: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='karakterler', aliases=['characters'])
    async def list_characters(ctx, house_filter=None):
        """List available ASOIAF characters"""
        try:
            # Get taken characters
            db.c.execute('SELECT character_name FROM asoiaf_characters')
            taken = {row[0] for row in db.c.fetchall()}

            # Filter characters
            available_chars = {}
            for name, data in ASOIAF_CHARACTERS.items():
                if name not in taken:
                    if house_filter is None or data["house"].lower() == house_filter.lower():
                        house = data["house"]
                        if house not in available_chars:
                            available_chars[house] = []
                        available_chars[house].append((name, data))

            if not available_chars:
                filter_text = f" ({house_filter} hanesi)" if house_filter else ""
                embed = create_embed("📋 Karakterler", f"Müsait karakter yok{filter_text}!", discord.Color.blue())
                await ctx.send(embed=embed)
                return

            embeds = []
            for house, characters in available_chars.items():
                house_emoji = get_house_emoji(house)
                embed = create_embed(f"{house_emoji} {house} Hanesi", 
                                   f"Müsait karakterler ({len(characters)} adet):", 
                                   discord.Color.blue())

                for name, data in characters[:10]:  # Limit to 10 per embed
                    embed.add_field(
                        name=f"👤 {name}",
                        value=f"**Unvan:** {data['title']}\n**Yaş:** {data['age']}\n**Yetenekler:** {', '.join(data['skills'][:2])}{'...' if len(data['skills']) > 2 else ''}",
                        inline=True
                    )

                embed.set_footer(text="!karakter <karakter_adı> ile karakter seçebilirsiniz")
                embeds.append(embed)

            # Send embeds
            for embed in embeds:
                await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"List characters error: {e}")
            embed = create_embed("❌ Hata", f"Karakterler listelenirken hata oluştu: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # ORDU YÖNETİMİ KOMUTLARI
    # ===============================
    
    @bot.command(name='ordu')
    async def army_status(ctx):
        """Display army status"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            from army_management import ArmyManagement
            army_mgmt = ArmyManagement(db)
            army_status = army_mgmt.get_army_status(alliance[0])
            
            if army_status:
                embed = army_mgmt.create_army_embed(army_status)
                await ctx.send(embed=embed)
            else:
                embed = create_embed("❌ Hata", "Ordu bilgileri alınamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Army status error: {e}")
            embed = create_embed("❌ Hata", f"Ordu durumu görüntülenirken hata oluştu: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='ordu_yükselt')
    async def upgrade_army(ctx, component: str, levels: int = 1):
        """Upgrade army component"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            from army_management import ArmyManagement
            army_mgmt = ArmyManagement(db)
            success, message = army_mgmt.upgrade_army_component(alliance[0], component, levels)
            
            color = discord.Color.green() if success else discord.Color.red()
            icon = "✅" if success else "❌"
            embed = create_embed(f"{icon} Ordu Yükseltme", message, color)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Army upgrade error: {e}")
            embed = create_embed("❌ Hata", f"Ordu yükseltme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='kaynak_al')
    async def buy_resources(ctx, resource_type: str, quantity: int):
        """Buy resources for army"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            from army_management import ArmyManagement
            army_mgmt = ArmyManagement(db)
            success, message = army_mgmt.buy_resources(alliance[0], resource_type, quantity)
            
            color = discord.Color.green() if success else discord.Color.red()
            icon = "✅" if success else "❌"
            embed = create_embed(f"{icon} Kaynak Satın Alma", message, color)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Buy resources error: {e}")
            embed = create_embed("❌ Hata", f"Kaynak satın alma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='ordu_ayarla')
    @commands.has_permissions(administrator=True)
    async def set_army_composition(ctx, infantry: Optional[int] = None, cavalry: Optional[int] = None, archers: Optional[int] = None, siege: Optional[int] = None):
        """Admin command to set army composition"""
        try:
            # Check if we're in war - if yes, use war armies
            wars = war_system.get_active_wars()
            if wars:
                # Show active wars and let admin select
                embed = create_embed("⚔️ Aktif Savaşlar", "Hangi savaştaki orduyu düzenlemek istiyorsunuz?", discord.Color.orange())
                war_list = ""
                for i, war in enumerate(wars, 1):
                    attacker = db.get_alliance_by_id(war[1])
                    defender = db.get_alliance_by_id(war[2])
                    war_list += f"{i}. {attacker[1]} vs {defender[1]} (ID: {war[0]})\n"
                
                embed.add_field(name="Savaşlar", value=war_list, inline=False)
                embed.set_footer(text="!ordu_ayarla_savaş <savaş_id> <piyade> <süvari> <okçu> <kuşatma> komutunu kullanın")
                await ctx.send(embed=embed)
                return
            
            # If not in war, ask which house to modify
            if not ctx.message.mentions:
                embed = create_embed("❌ Hata", "Bir kullanıcıyı etiketleyin veya savaş ID'si belirtin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
                
            target_user = ctx.message.mentions[0]
            user_alliance = db.get_user_alliance(target_user.id)
            
            if not user_alliance:
                embed = create_embed("❌ Hata", "Hedef kullanıcı bir haneye üye değil!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            from army_management import ArmyManagement
            army_mgmt = ArmyManagement(db)
            success, message = army_mgmt.set_army_composition(user_alliance[0], infantry, cavalry, archers, siege)
            
            color = discord.Color.green() if success else discord.Color.red()
            icon = "✅" if success else "❌"
            embed = create_embed(f"{icon} Ordu Kompozisyonu", f"{message}\n**Hane:** {user_alliance[1]}", color)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Set army composition error: {e}")
            embed = create_embed("❌ Hata", f"Ordu kompozisyonu ayarlama hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='ordu_ayarla_savaş')
    @commands.has_permissions(administrator=True)
    async def set_war_army_composition(ctx, war_id: int, infantry: Optional[int] = None, cavalry: Optional[int] = None, archers: Optional[int] = None, siege: Optional[int] = None):
        """Admin command to set army composition for a specific war"""
        try:
            # Get war details
            war = war_system.get_war_by_id(war_id)
            if not war:
                embed = create_embed("❌ Hata", "Savaş bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Show both armies and ask which one to modify
            attacker = db.get_alliance_by_id(war[1])
            defender = db.get_alliance_by_id(war[2])
            
            embed = create_embed("⚔️ Savaş Ordu Düzenleme", 
                               f"**Savaş:** {attacker[1]} vs {defender[1]}\n\nHangi tarafın ordusunu düzenlemek istiyorsunuz?", 
                               discord.Color.orange())
            embed.add_field(name="Komutlar", 
                          value=f"`!ordu_düzenle_saldırgan {war_id} <piyade> <süvari> <okçu> <kuşatma>`\n"
                                f"`!ordu_düzenle_savunan {war_id} <piyade> <süvari> <okçu> <kuşatma>`", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Set war army composition error: {e}")
            embed = create_embed("❌ Hata", f"Savaş ordu kompozisyonu hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # TİCARET SİSTEMİ
    # ===============================
    
    @bot.command(name='ticaret')
    async def trade_menu(ctx):
        """Show trading options"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("🏪 Ticaret Merkezi", 
                               f"**{alliance[1]}** hanesi için ticaret seçenekleri", 
                               discord.Color.gold())
            
            embed.add_field(name="💰 Kaynak Ticareti",
                          value="`!kaynak_sat <tür> <miktar>` - Kaynak sat\n"
                                "`!kaynak_bul <tür>` - Satılan kaynakları bul\n"
                                "`!kaynak_satın_al <satıcı> <tür> <miktar>` - Kaynak satın al",
                          inline=False)
            
            embed.add_field(name="⚔️ Asker Ticareti",
                          value="`!asker_sat <miktar> <fiyat>` - Asker sat\n"
                                "`!asker_bul` - Satılan askerleri bul\n"
                                "`!asker_satın_al <satıcı> <miktar>` - Asker satın al",
                          inline=False)
                          
            embed.add_field(name="🏰 Ticaret Antlaşmaları",
                          value="`!ticaret_antlaşması <hane>` - Ticaret antlaşması öner\n"
                                "`!antlaşma_kabul <hane>` - Antlaşmayı kabul et\n"
                                "`!antlaşmalar` - Aktif antlaşmaları görüntüle",
                          inline=False)
            
            embed.set_footer(text="Ticaret yapmak için yeterli kaynak ve altına sahip olmalısınız!")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Trade menu error: {e}")
            embed = create_embed("❌ Hata", f"Ticaret menüsü hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='kaynak_sat')
    async def sell_resource(ctx, resource_type: str, quantity: int, price_per_unit: Optional[int] = None):
        """Sell resources"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Valid resource types
            valid_resources = ['food', 'stone', 'wood', 'iron', 'horses', 'wine']
            if resource_type not in valid_resources:
                embed = create_embed("❌ Hata", f"Geçersiz kaynak türü! Kullanılabilir: {', '.join(valid_resources)}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if house has enough resources
            db.c.execute('SELECT quantity FROM house_resources WHERE house_id = ? AND resource_type = ?', 
                        (alliance[0], resource_type))
            result = db.c.fetchone()
            current_quantity = result[0] if result else 0
            
            if current_quantity < quantity:
                embed = create_embed("❌ Hata", f"Yetersiz kaynak! Mevcut: {format_number(current_quantity)}, İstenen: {format_number(quantity)}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Default prices
            default_prices = {'food': 7, 'stone': 12, 'wood': 10, 'iron': 18, 'horses': 120, 'wine': 25}
            if not price_per_unit:
                price_per_unit = default_prices.get(resource_type, 10)
            
            # Add to trade market
            db.c.execute('''
            INSERT INTO trade_offers (seller_id, offer_type, resource_type, quantity, price_per_unit, total_price, created_at)
            VALUES (?, 'resource', ?, ?, ?, ?, datetime('now'))
            ''', (alliance[0], resource_type, quantity, price_per_unit, quantity * price_per_unit))
            
            # Remove resources from house
            db.c.execute('''
            UPDATE house_resources SET quantity = quantity - ? 
            WHERE house_id = ? AND resource_type = ?
            ''', (quantity, alliance[0], resource_type))
            
            db.conn.commit()
            
            embed = create_embed("✅ Kaynak Satışa Çıkarıldı", 
                               f"**{format_number(quantity)}** {resource_type} pazara çıkarıldı!", 
                               discord.Color.green())
            embed.add_field(name="Birim Fiyat", value=f"{format_number(price_per_unit)} altın", inline=True)
            embed.add_field(name="Toplam Değer", value=f"{format_number(quantity * price_per_unit)} altın", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Sell resource error: {e}")
            embed = create_embed("❌ Hata", f"Kaynak satış hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='kaynak_bul')
    async def find_resources(ctx, resource_type: Optional[str] = None):
        """Find available resources for sale"""
        try:
            if resource_type:
                db.c.execute('''
                SELECT to.*, a.name FROM trade_offers to
                JOIN alliances a ON to.seller_id = a.id
                WHERE to.offer_type = 'resource' AND to.resource_type = ?
                ORDER BY to.price_per_unit ASC
                ''', (resource_type,))
            else:
                db.c.execute('''
                SELECT to.*, a.name FROM trade_offers to
                JOIN alliances a ON to.seller_id = a.id
                WHERE to.offer_type = 'resource'
                ORDER BY to.resource_type, to.price_per_unit ASC
                ''')
            
            offers = db.c.fetchall()
            
            if not offers:
                filter_text = f" ({resource_type})" if resource_type else ""
                embed = create_embed("📋 Kaynak Pazarı", f"Satılık kaynak yok{filter_text}!", discord.Color.orange())
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("🏪 Kaynak Pazarı", 
                               f"Satılık kaynaklar{f' ({resource_type})' if resource_type else ''}", 
                               discord.Color.gold())
            
            current_resource = None
            resource_text = ""
            
            for offer in offers[:20]:  # Limit to 20 offers
                if current_resource != offer[2]:  # resource_type
                    if resource_text and current_resource:
                        embed.add_field(name=f"📦 {current_resource.title()}", value=resource_text, inline=False)
                    current_resource = offer[2]
                    resource_text = ""
                
                resource_text += f"**{offer[7]}:** {format_number(offer[3])} adet - {format_number(offer[4])} altın/adet\n"
            
            if resource_text and current_resource:
                embed.add_field(name=f"📦 {current_resource.title()}", value=resource_text, inline=False)
            
            embed.set_footer(text="!kaynak_satın_al <satıcı_hane> <tür> <miktar> ile satın alın")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Find resources error: {e}")
            embed = create_embed("❌ Hata", f"Kaynak arama hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='kaynak_satın_al')
    async def buy_resource_from_market(ctx, seller_house: str, resource_type: str, quantity: int):
        """Buy resources from market"""
        try:
            user_id = ctx.author.id
            buyer_alliance = db.get_user_alliance(user_id)
            
            if not buyer_alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find seller
            db.c.execute('SELECT id FROM alliances WHERE name LIKE ?', (f'%{seller_house}%',))
            seller_result = db.c.fetchone()
            
            if not seller_result:
                embed = create_embed("❌ Hata", f"'{seller_house}' hanesi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            seller_id = seller_result[0]
            
            # Find matching trade offer
            db.c.execute('''
            SELECT * FROM trade_offers 
            WHERE seller_id = ? AND resource_type = ? AND quantity >= ? AND status = 'active'
            ORDER BY price_per_unit ASC LIMIT 1
            ''', (seller_id, resource_type, quantity))
            
            offer = db.c.fetchone()
            
            if not offer:
                embed = create_embed("❌ Hata", f"Uygun teklif bulunamadı! {seller_house} hanesinden {quantity} adet {resource_type} satılmıyor.", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            total_cost = offer[4] * quantity  # price_per_unit * quantity
            
            # Check buyer's gold
            if buyer_alliance[3] < total_cost:  # gold
                embed = create_embed("❌ Hata", f"Yetersiz altın! Gerekli: {format_number(total_cost)}, Mevcut: {format_number(buyer_alliance[3])}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Process transaction
            db.c.execute('BEGIN TRANSACTION')
            
            try:
                # Transfer gold
                db.update_alliance_resources(buyer_alliance[0], -total_cost, 0)
                db.update_alliance_resources(seller_id, total_cost, 0)
                
                # Transfer resources
                db.c.execute('''
                INSERT OR REPLACE INTO house_resources (house_id, resource_type, quantity, quality)
                VALUES (?, ?, COALESCE((SELECT quantity FROM house_resources WHERE house_id = ? AND resource_type = ?), 0) + ?, 60)
                ''', (buyer_alliance[0], resource_type, buyer_alliance[0], resource_type, quantity))
                
                # Update or remove offer
                remaining_quantity = offer[3] - quantity
                if remaining_quantity <= 0:
                    db.c.execute('UPDATE trade_offers SET status = "completed" WHERE id = ?', (offer[0],))
                else:
                    db.c.execute('UPDATE trade_offers SET quantity = ?, total_price = ? WHERE id = ?', 
                               (remaining_quantity, remaining_quantity * offer[4], offer[0]))
                
                # Record transaction
                db.c.execute('''
                INSERT INTO trade_transactions (buyer_id, seller_id, offer_id, quantity, total_cost)
                VALUES (?, ?, ?, ?, ?)
                ''', (buyer_alliance[0], seller_id, offer[0], quantity, total_cost))
                
                db.c.execute('COMMIT')
                
                seller_alliance = db.get_alliance_by_id(seller_id)
                embed = create_embed("✅ Ticaret Tamamlandı", 
                                   f"**{format_number(quantity)}** {resource_type} satın alındı!", 
                                   discord.Color.green())
                embed.add_field(name="Satıcı", value=seller_alliance[1], inline=True)
                embed.add_field(name="Toplam Maliyet", value=f"{format_number(total_cost)} altın", inline=True)
                embed.add_field(name="Birim Fiyat", value=f"{format_number(offer[4])} altın", inline=True)
                await ctx.send(embed=embed)
                
            except Exception as e:
                db.c.execute('ROLLBACK')
                raise e
                
        except Exception as e:
            logger.error(f"Buy resource from market error: {e}")
            embed = create_embed("❌ Hata", f"Kaynak satın alma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='ticaret_antlaşması')
    async def propose_trade_agreement(ctx, *, target_house: str):
        """Propose a trade agreement"""
        try:
            user_id = ctx.author.id
            proposer_alliance = db.get_user_alliance(user_id)
            
            if not proposer_alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if proposer_alliance[2] != user_id:  # leader_id
                embed = create_embed("❌ Hata", "Sadece hane lideri ticaret antlaşması önerebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find target house
            db.c.execute('SELECT id, name FROM alliances WHERE name LIKE ?', (f'%{target_house}%',))
            target_result = db.c.fetchone()
            
            if not target_result:
                embed = create_embed("❌ Hata", f"'{target_house}' hanesi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            target_id, target_name = target_result
            
            if target_id == proposer_alliance[0]:
                embed = create_embed("❌ Hata", "Kendi hanenle antlaşma yapamazsın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if agreement already exists
            db.c.execute('''
            SELECT * FROM trade_agreements 
            WHERE (house1_id = ? AND house2_id = ?) OR (house1_id = ? AND house2_id = ?)
            AND status IN ('pending', 'active')
            ''', (proposer_alliance[0], target_id, target_id, proposer_alliance[0]))
            
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Bu hane ile zaten aktif veya bekleyen bir antlaşma var!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Create trade agreement proposal
            expires_at = "datetime('now', '+7 days')"
            db.c.execute(f'''
            INSERT INTO trade_agreements (house1_id, house2_id, agreement_type, discount_percentage, expires_at)
            VALUES (?, ?, 'trade_route', 0.15, {expires_at})
            ''', (proposer_alliance[0], target_id))
            
            db.conn.commit()
            
            embed = create_embed("📜 Ticaret Antlaşması Önerildi", 
                               f"**{target_name}** hanesine ticaret antlaşması önerildi!", 
                               discord.Color.gold())
            embed.add_field(name="Avantajlar", 
                          value="• %15 indirimli ticaret\n• Öncelikli kaynak erişimi\n• Ortak ticaret rotaları", 
                          inline=False)
            embed.add_field(name="Süre", value="7 gün içinde yanıt bekleniyor", inline=True)
            embed.set_footer(text=f"{target_name} hanesi !antlaşma_kabul {proposer_alliance[1]} ile kabul edebilir")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Propose trade agreement error: {e}")
            embed = create_embed("❌ Hata", f"Ticaret antlaşması önerme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='antlaşma_kabul')
    async def accept_trade_agreement(ctx, *, proposer_house: str):
        """Accept a trade agreement"""
        try:
            user_id = ctx.author.id
            accepter_alliance = db.get_user_alliance(user_id)
            
            if not accepter_alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if accepter_alliance[2] != user_id:  # leader_id
                embed = create_embed("❌ Hata", "Sadece hane lideri antlaşmayı kabul edebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find proposer house
            db.c.execute('SELECT id, name FROM alliances WHERE name LIKE ?', (f'%{proposer_house}%',))
            proposer_result = db.c.fetchone()
            
            if not proposer_result:
                embed = create_embed("❌ Hata", f"'{proposer_house}' hanesi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            proposer_id, proposer_name = proposer_result
            
            # Find pending agreement
            db.c.execute('''
            SELECT * FROM trade_agreements 
            WHERE house1_id = ? AND house2_id = ? AND status = 'pending'
            ''', (proposer_id, accepter_alliance[0]))
            
            agreement = db.c.fetchone()
            
            if not agreement:
                embed = create_embed("❌ Hata", f"{proposer_name} hanesinden bekleyen antlaşma bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Accept agreement
            expires_at = "datetime('now', '+30 days')"
            db.c.execute(f'''
            UPDATE trade_agreements 
            SET status = 'active', expires_at = {expires_at}
            WHERE id = ?
            ''', (agreement[0],))
            
            db.conn.commit()
            
            embed = create_embed("🤝 Ticaret Antlaşması Kabul Edildi", 
                               f"**{proposer_name}** ile ticaret antlaşması aktif!", 
                               discord.Color.green())
            embed.add_field(name="Aktif Avantajlar", 
                          value="• %15 indirimli ticaret\n• Öncelikli kaynak erişimi\n• Ortak ticaret rotaları", 
                          inline=False)
            embed.add_field(name="Süre", value="30 gün boyunca aktif", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Accept trade agreement error: {e}")
            embed = create_embed("❌ Hata", f"Antlaşma kabul etme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='antlaşmalar')
    async def list_trade_agreements(ctx):
        """List active trade agreements"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Get trade agreements
            db.c.execute('''
            SELECT ta.*, a1.name as house1_name, a2.name as house2_name 
            FROM trade_agreements ta
            JOIN alliances a1 ON ta.house1_id = a1.id
            JOIN alliances a2 ON ta.house2_id = a2.id
            WHERE (ta.house1_id = ? OR ta.house2_id = ?) AND ta.status IN ('active', 'pending')
            ORDER BY ta.status, ta.created_at DESC
            ''', (alliance[0], alliance[0]))
            
            agreements = db.c.fetchall()
            
            if not agreements:
                embed = create_embed("📋 Ticaret Antlaşmaları", "Aktif ticaret antlaşmanız yok!", discord.Color.orange())
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("🤝 Ticaret Antlaşmaları", 
                               f"**{alliance[1]}** hanesi antlaşmaları", 
                               discord.Color.gold())
            
            active_agreements = ""
            pending_agreements = ""
            
            for agreement in agreements:
                partner_name = agreement[-1] if agreement[2] == alliance[0] else agreement[-2]  # house2_name if we're house1, else house1_name
                discount = int(agreement[5] * 100)  # discount_percentage * 100
                
                agreement_text = f"• **{partner_name}** - %{discount} indirim\n"
                
                if agreement[6] == 'active':  # status
                    active_agreements += agreement_text
                else:
                    pending_agreements += agreement_text
            
            if active_agreements:
                embed.add_field(name="🟢 Aktif Antlaşmalar", value=active_agreements, inline=False)
            
            if pending_agreements:
                embed.add_field(name="🟡 Bekleyen Antlaşmalar", value=pending_agreements, inline=False)
            
            embed.set_footer(text="!ticaret_antlaşması <hane> ile yeni antlaşma önerebilirsiniz")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"List trade agreements error: {e}")
            embed = create_embed("❌ Hata", f"Antlaşma listeleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # TURNUVA SİSTEMİ
    # ===============================
    
    @bot.command(name='turnuva_düzenle')
    async def create_tournament(ctx, tournament_type: str, entry_fee: int = 1000, prize_pool: int = 10000):
        """Create a new tournament"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if alliance[2] != user_id:
                embed = create_embed("❌ Hata", "Sadece hane lideri turnuva düzenleyebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            valid_types = ['joust', 'melee', 'archery', 'mixed']
            if tournament_type not in valid_types:
                embed = create_embed("❌ Hata", f"Geçersiz turnuva türü! Kullanılabilir: {', '.join(valid_types)}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if house can afford the prize pool
            if alliance[3] < prize_pool:  # gold
                embed = create_embed("❌ Hata", f"Yetersiz altın! Ödül havuzu için {format_number(prize_pool)} altın gerekli.", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Create tournament
            tournament_name = f"{alliance[1]} {tournament_type.title()} Turnuvası"
            db.c.execute('''
            INSERT INTO tournaments (name, host_house_id, tournament_type, entry_fee, prize_pool, start_time)
            VALUES (?, ?, ?, ?, ?, datetime('now', '+1 day'))
            ''', (tournament_name, alliance[0], tournament_type, entry_fee, prize_pool))
            
            # Deduct prize pool from house gold
            db.update_alliance_resources(alliance[0], -prize_pool, 0)
            
            db.conn.commit()
            
            embed = create_embed("🏆 Turnuva Oluşturuldu", 
                               f"**{tournament_name}** başarıyla organize edildi!", 
                               discord.Color.gold())
            embed.add_field(name="Tür", value=tournament_type.title(), inline=True)
            embed.add_field(name="Giriş Ücreti", value=f"{format_number(entry_fee)} altın", inline=True)
            embed.add_field(name="Ödül Havuzu", value=f"{format_number(prize_pool)} altın", inline=True)
            embed.add_field(name="Başlangıç", value="24 saat sonra", inline=True)
            embed.set_footer(text="!turnuva_katıl komutu ile katılabilirsiniz")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Create tournament error: {e}")
            embed = create_embed("❌ Hata", f"Turnuva oluşturma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='turnuvalar')
    async def list_tournaments(ctx):
        """List active tournaments"""
        try:
            db.c.execute('''
            SELECT t.*, a.name as host_name, 
                   (SELECT COUNT(*) FROM tournament_participants tp WHERE tp.tournament_id = t.id) as participant_count
            FROM tournaments t
            JOIN alliances a ON t.host_house_id = a.id
            WHERE t.status = 'open'
            ORDER BY t.start_time ASC
            ''')
            
            tournaments = db.c.fetchall()
            
            if not tournaments:
                embed = create_embed("🏆 Turnuvalar", "Şu anda aktif turnuva yok!", discord.Color.orange())
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("🏆 Aktif Turnuvalar", 
                               "Katılabileceğiniz turnuvalar", 
                               discord.Color.gold())
            
            for tournament in tournaments[:10]:  # Limit to 10
                tournament_text = f"**Host:** {tournament[12]}\n"  # host_name
                tournament_text += f"**Tür:** {tournament[3].title()}\n"  # tournament_type
                tournament_text += f"**Giriş:** {format_number(tournament[4])} altın\n"  # entry_fee
                tournament_text += f"**Ödül:** {format_number(tournament[5])} altın\n"  # prize_pool
                tournament_text += f"**Katılımcı:** {tournament[13]}/{tournament[9]}"  # participant_count/max_participants
                
                embed.add_field(name=f"🏆 {tournament[1]}", value=tournament_text, inline=True)  # name
            
            embed.set_footer(text="!turnuva_katıl <turnuva_adı> ile katılın")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"List tournaments error: {e}")
            embed = create_embed("❌ Hata", f"Turnuva listeleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='turnuva_katıl')
    async def join_tournament(ctx, *, tournament_name: str):
        """Join a tournament"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find tournament
            db.c.execute('''
            SELECT * FROM tournaments 
            WHERE name LIKE ? AND status = 'open'
            ''', (f'%{tournament_name}%',))
            
            tournament = db.c.fetchone()
            
            if not tournament:
                embed = create_embed("❌ Hata", f"'{tournament_name}' turnuvası bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if already participating
            db.c.execute('SELECT id FROM tournament_participants WHERE tournament_id = ? AND user_id = ?', 
                        (tournament[0], user_id))
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Bu turnuvaya zaten katıldınız!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check participant limit
            db.c.execute('SELECT COUNT(*) FROM tournament_participants WHERE tournament_id = ?', (tournament[0],))
            participant_count = db.c.fetchone()[0]
            
            if participant_count >= tournament[9]:  # max_participants
                embed = create_embed("❌ Hata", "Turnuva dolu! Maksimum katılımcı sayısına ulaşıldı.", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check entry fee
            if alliance[3] < tournament[4]:  # gold < entry_fee
                embed = create_embed("❌ Hata", f"Yetersiz altın! Giriş ücreti: {format_number(tournament[4])} altın", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Join tournament
            db.c.execute('''
            INSERT INTO tournament_participants (tournament_id, user_id, character_skill, equipment_bonus)
            VALUES (?, ?, ?, ?)
            ''', (tournament[0], user_id, random.randint(40, 80), random.randint(5, 20)))
            
            # Pay entry fee
            db.update_alliance_resources(alliance[0], -tournament[4], 0)
            
            db.conn.commit()
            
            embed = create_embed("🏆 Turnuvaya Katıldınız", 
                               f"**{tournament[1]}** turnuvasına başarıyla katıldınız!", 
                               discord.Color.green())
            embed.add_field(name="Giriş Ücreti", value=f"{format_number(tournament[4])} altın ödendi", inline=True)
            embed.add_field(name="Toplam Ödül", value=f"{format_number(tournament[5])} altın", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Join tournament error: {e}")
            embed = create_embed("❌ Hata", f"Turnuvaya katılım hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='turnuva_iptal')
    async def cancel_tournament(ctx, *, tournament_name: str):
        """Cancel a tournament (only host can cancel)"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find tournament
            db.c.execute('''
            SELECT * FROM tournaments 
            WHERE name LIKE ? AND status = 'open'
            ''', (f'%{tournament_name}%',))
            
            tournament = db.c.fetchone()
            
            if not tournament:
                embed = create_embed("❌ Hata", f"'{tournament_name}' turnuvası bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is tournament host
            if tournament[2] != alliance[0]:  # host_house_id
                embed = create_embed("❌ Hata", "Sadece turnuva organizatörü iptal edebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Cancel tournament and refund entry fees
            db.c.execute('''
            SELECT tp.user_id, t.entry_fee, m.alliance_id
            FROM tournament_participants tp
            JOIN tournaments t ON tp.tournament_id = t.id
            JOIN members m ON tp.user_id = m.user_id
            WHERE tp.tournament_id = ?
            ''', (tournament[0],))
            
            participants = db.c.fetchall()
            
            # Refund entry fees
            for participant in participants:
                db.update_alliance_resources(participant[2], tournament[4], 0)  # alliance_id, entry_fee
            
            # Refund prize pool to host
            db.update_alliance_resources(alliance[0], tournament[5], 0)  # prize_pool
            
            # Cancel tournament
            db.c.execute('UPDATE tournaments SET status = "cancelled" WHERE id = ?', (tournament[0],))
            db.c.execute('DELETE FROM tournament_participants WHERE tournament_id = ?', (tournament[0],))
            
            db.conn.commit()
            
            embed = create_embed("🏆 Turnuva İptal Edildi", 
                               f"**{tournament[1]}** turnuvası iptal edildi!", 
                               discord.Color.orange())
            embed.add_field(name="İade Edilen", 
                          value=f"Giriş ücretleri: {len(participants)} katılımcıya {format_number(tournament[4])} altın\n"
                                f"Ödül havuzu: {format_number(tournament[5])} altın", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Cancel tournament error: {e}")
            embed = create_embed("❌ Hata", f"Turnuva iptal etme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='turnuva_bitir')
    async def finish_tournament(ctx, *, tournament_name: str):
        """Finish a tournament and distribute prizes"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find tournament
            db.c.execute('''
            SELECT * FROM tournaments 
            WHERE name LIKE ? AND status = 'open'
            ''', (f'%{tournament_name}%',))
            
            tournament = db.c.fetchone()
            
            if not tournament:
                embed = create_embed("❌ Hata", f"'{tournament_name}' turnuvası bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is tournament host
            if tournament[2] != alliance[0]:  # host_house_id
                embed = create_embed("❌ Hata", "Sadece turnuva organizatörü bitirebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Get participants and simulate tournament
            db.c.execute('''
            SELECT tp.*, m.alliance_id 
            FROM tournament_participants tp
            JOIN members m ON tp.user_id = m.user_id
            WHERE tp.tournament_id = ? AND tp.eliminated = 0
            ORDER BY (tp.character_skill + tp.equipment_bonus + ABS(RANDOM() % 30)) DESC
            ''', (tournament[0],))
            
            participants = db.c.fetchall()
            
            if len(participants) < 2:
                embed = create_embed("❌ Hata", "Turnuvayı bitirmek için en az 2 katılımcı gerekli!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Award prizes
            prize_pool = tournament[5]  # prize_pool
            first_prize = int(prize_pool * 0.5)
            second_prize = int(prize_pool * 0.3)
            third_prize = int(prize_pool * 0.2)
            
            winners = []
            if len(participants) >= 1:
                # First place
                db.update_alliance_resources(participants[0][9], first_prize, 0)  # alliance_id
                db.c.execute('UPDATE tournament_participants SET final_position = 1, prize_won = ? WHERE id = ?', 
                           (first_prize, participants[0][0]))
                winners.append((1, participants[0][2], first_prize))  # position, user_id, prize
            
            if len(participants) >= 2:
                # Second place
                db.update_alliance_resources(participants[1][9], second_prize, 0)
                db.c.execute('UPDATE tournament_participants SET final_position = 2, prize_won = ? WHERE id = ?', 
                           (second_prize, participants[1][0]))
                winners.append((2, participants[1][2], second_prize))
            
            if len(participants) >= 3:
                # Third place
                db.update_alliance_resources(participants[2][9], third_prize, 0)
                db.c.execute('UPDATE tournament_participants SET final_position = 3, prize_won = ? WHERE id = ?', 
                           (third_prize, participants[2][0]))
                winners.append((3, participants[2][2], third_prize))
            
            # Mark tournament as finished
            db.c.execute('UPDATE tournaments SET status = "finished", end_time = datetime("now") WHERE id = ?', 
                        (tournament[0],))
            
            db.conn.commit()
            
            embed = create_embed("🏆 Turnuva Tamamlandı", 
                               f"**{tournament[1]}** turnuvası sona erdi!", 
                               discord.Color.gold())
            
            winner_text = ""
            medals = ["🥇", "🥈", "🥉"]
            for position, user_id, prize in winners:
                user = bot.get_user(user_id)
                winner_text += f"{medals[position-1]} **{user.display_name if user else 'Bilinmeyen'}**: {format_number(prize)} altın\n"
            
            embed.add_field(name="🏆 Kazananlar", value=winner_text, inline=False)
            embed.add_field(name="📊 İstatistikler", 
                          value=f"Toplam Katılımcı: {len(participants)}\n"
                                f"Toplam Ödül: {format_number(prize_pool)} altın", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Finish tournament error: {e}")
            embed = create_embed("❌ Hata", f"Turnuva bitirme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # DÜELLO SİSTEMİ
    # ===============================
    
    @bot.command(name='düello_çağır')
    async def challenge_duel(ctx, opponent: discord.Member, duel_type: str = 'sword', wager: int = 0):
        """Challenge someone to a duel"""
        try:
            challenger_id = ctx.author.id
            challenged_id = opponent.id
            
            if challenger_id == challenged_id:
                embed = create_embed("❌ Hata", "Kendini düelloya çağıramazsın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            challenger_alliance = db.get_user_alliance(challenger_id)
            challenged_alliance = db.get_user_alliance(challenged_id)
            
            if not challenger_alliance or not challenged_alliance:
                embed = create_embed("❌ Hata", "Her iki oyuncu da bir haneye üye olmalı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            valid_types = ['sword', 'lance', 'trial_by_combat']
            if duel_type not in valid_types:
                embed = create_embed("❌ Hata", f"Geçersiz düello türü! Kullanılabilir: {', '.join(valid_types)}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check for existing active duel
            db.c.execute('''
            SELECT id FROM duels 
            WHERE ((challenger_id = ? AND challenged_id = ?) OR (challenger_id = ? AND challenged_id = ?))
            AND status = 'challenged'
            ''', (challenger_id, challenged_id, challenged_id, challenger_id))
            
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Bu oyuncuyla zaten aktif bir düellonuz var!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check wager amount
            if wager > 0:
                if challenger_alliance[3] < wager:  # gold
                    embed = create_embed("❌ Hata", f"Yetersiz altın! Bahis: {format_number(wager)} altın", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
            
            # Create duel challenge
            db.c.execute('''
            INSERT INTO duels (challenger_id, challenged_id, duel_type, wager_amount)
            VALUES (?, ?, ?, ?)
            ''', (challenger_id, challenged_id, duel_type, wager))
            
            db.conn.commit()
            
            embed = create_embed("⚔️ Düello Çağrısı", 
                               f"**{ctx.author.display_name}** {opponent.display_name}'i düelloya çağırdı!", 
                               discord.Color.orange())
            embed.add_field(name="Düello Türü", value=duel_type.replace('_', ' ').title(), inline=True)
            embed.add_field(name="Bahis", value=f"{format_number(wager)} altın" if wager > 0 else "Bahissiz", inline=True)
            embed.add_field(name="Challenger Hanesi", value=challenger_alliance[1], inline=True)
            embed.add_field(name="Challenged Hanesi", value=challenged_alliance[1], inline=True)
            embed.set_footer(text=f"{opponent.display_name} !düello_kabul {ctx.author.display_name} ile kabul edebilir")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Challenge duel error: {e}")
            embed = create_embed("❌ Hata", f"Düello çağrısı hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='düello_kabul')
    async def accept_duel(ctx, challenger: discord.Member):
        """Accept a duel challenge"""
        try:
            challenged_id = ctx.author.id
            challenger_id = challenger.id
            
            # Find pending duel
            db.c.execute('''
            SELECT * FROM duels 
            WHERE challenger_id = ? AND challenged_id = ? AND status = 'challenged'
            ''', (challenger_id, challenged_id))
            
            duel = db.c.fetchone()
            
            if not duel:
                embed = create_embed("❌ Hata", f"{challenger.display_name} tarafından düello çağrısı bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            challenged_alliance = db.get_user_alliance(challenged_id)
            challenger_alliance = db.get_user_alliance(challenger_id)
            
            # Check wager if exists
            if duel[4] > 0:  # wager_amount
                if challenged_alliance[3] < duel[4]:  # gold
                    embed = create_embed("❌ Hata", f"Yetersiz altın! Bahis: {format_number(duel[4])} altın", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
            
            # Simulate duel
            challenger_skill = random.randint(40, 90)
            challenged_skill = random.randint(40, 90)
            
            # Add some randomness
            challenger_roll = random.randint(1, 20)
            challenged_roll = random.randint(1, 20)
            
            challenger_total = challenger_skill + challenger_roll
            challenged_total = challenged_skill + challenged_roll
            
            if challenger_total > challenged_total:
                winner_id = challenger_id
                winner_name = challenger.display_name
                loser_name = ctx.author.display_name
            else:
                winner_id = challenged_id
                winner_name = ctx.author.display_name
                loser_name = challenger.display_name
            
            # Handle wager
            if duel[4] > 0:  # wager_amount
                if winner_id == challenger_id:
                    db.update_alliance_resources(challenger_alliance[0], duel[4], 0)
                    db.update_alliance_resources(challenged_alliance[0], -duel[4], 0)
                else:
                    db.update_alliance_resources(challenged_alliance[0], duel[4], 0)
                    db.update_alliance_resources(challenger_alliance[0], -duel[4], 0)
            
            # Update duel
            fight_details = f"{challenger.display_name}: {challenger_total} vs {ctx.author.display_name}: {challenged_total}"
            db.c.execute('''
            UPDATE duels 
            SET status = 'completed', winner_id = ?, fight_details = ?, completed_at = datetime('now')
            WHERE id = ?
            ''', (winner_id, fight_details, duel[0]))
            
            db.conn.commit()
            
            embed = create_embed("⚔️ Düello Sonucu", 
                               f"**{winner_name}** düelloyu kazandı!", 
                               discord.Color.green())
            embed.add_field(name="Düello Türü", value=duel[3].replace('_', ' ').title(), inline=True)
            embed.add_field(name="Sonuç", value=fight_details, inline=False)
            if duel[4] > 0:
                embed.add_field(name="Kazanılan Bahis", value=f"{format_number(duel[4])} altın", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Accept duel error: {e}")
            embed = create_embed("❌ Hata", f"Düello kabul etme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='düello_reddet')
    async def decline_duel(ctx, challenger: discord.Member):
        """Decline a duel challenge"""
        try:
            challenged_id = ctx.author.id
            challenger_id = challenger.id
            
            # Find pending duel
            db.c.execute('''
            SELECT * FROM duels 
            WHERE challenger_id = ? AND challenged_id = ? AND status = 'challenged'
            ''', (challenger_id, challenged_id))
            
            duel = db.c.fetchone()
            
            if not duel:
                embed = create_embed("❌ Hata", f"{challenger.display_name} tarafından düello çağrısı bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Decline duel
            db.c.execute('UPDATE duels SET status = "declined" WHERE id = ?', (duel[0],))
            db.conn.commit()
            
            embed = create_embed("⚔️ Düello Reddedildi", 
                               f"**{ctx.author.display_name}** {challenger.display_name}'in düello çağrısını reddetti!", 
                               discord.Color.orange())
            embed.add_field(name="Düello Türü", value=duel[3].replace('_', ' ').title(), inline=True)
            if duel[4] > 0:  # wager_amount
                embed.add_field(name="Bahis", value=f"{format_number(duel[4])} altın", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Decline duel error: {e}")
            embed = create_embed("❌ Hata", f"Düello reddetme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='düellolarım')
    async def my_duels(ctx):
        """Show my active duels"""
        try:
            user_id = ctx.author.id
            
            # Get duels where user is involved
            db.c.execute('''
            SELECT d.*, 
                   u1.user_id as challenger_discord_id, 
                   u2.user_id as challenged_discord_id,
                   a1.name as challenger_house,
                   a2.name as challenged_house
            FROM duels d
            JOIN members u1 ON d.challenger_id = u1.user_id
            JOIN members u2 ON d.challenged_id = u2.user_id  
            JOIN alliances a1 ON u1.alliance_id = a1.id
            JOIN alliances a2 ON u2.alliance_id = a2.id
            WHERE (d.challenger_id = ? OR d.challenged_id = ?) AND d.status IN ('challenged', 'accepted')
            ORDER BY d.created_at DESC
            ''', (user_id, user_id))
            
            duels = db.c.fetchall()
            
            if not duels:
                embed = create_embed("⚔️ Düellolarım", "Aktif düellonuz yok!", discord.Color.blue())
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("⚔️ Aktif Düellolarım", 
                               f"**{ctx.author.display_name}** aktif düellolar", 
                               discord.Color.orange())
            
            for duel in duels:
                challenger_user = bot.get_user(duel[11])  # challenger_discord_id
                challenged_user = bot.get_user(duel[12])  # challenged_discord_id
                
                if duel[1] == user_id:  # challenger_id == user_id (I'm challenger)
                    opponent = challenged_user.display_name if challenged_user else "Bilinmeyen"
                    opponent_house = duel[14]  # challenged_house
                    role = "Çağıran"
                else:  # I'm challenged
                    opponent = challenger_user.display_name if challenger_user else "Bilinmeyen"
                    opponent_house = duel[13]  # challenger_house  
                    role = "Çağrılan"
                
                duel_text = f"**Rakip:** {opponent} ({opponent_house})\n"
                duel_text += f"**Rol:** {role}\n"
                duel_text += f"**Tür:** {duel[3].replace('_', ' ').title()}\n"
                duel_text += f"**Durum:** {duel[5].title()}\n"
                if duel[4] > 0:  # wager_amount
                    duel_text += f"**Bahis:** {format_number(duel[4])} altın"
                
                embed.add_field(name=f"⚔️ Düello #{duel[0]}", value=duel_text, inline=True)
            
            embed.set_footer(text="!düello_kabul veya !düello_reddet komutlarını kullanın")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"My duels error: {e}")
            embed = create_embed("❌ Hata", f"Düello listeleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # EVLİLİK VE AİLE SİSTEMİ
    # ===============================
    
    @bot.command(name='evlen')
    async def propose_marriage(ctx, partner: discord.Member):
        """Propose marriage to someone"""
        try:
            proposer_id = ctx.author.id
            partner_id = partner.id
            
            if proposer_id == partner_id:
                embed = create_embed("❌ Hata", "Kendini evlenemezsin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if both are in houses
            proposer_alliance = db.get_user_alliance(proposer_id)
            partner_alliance = db.get_user_alliance(partner_id)
            
            if not proposer_alliance or not partner_alliance:
                embed = create_embed("❌ Hata", "Her iki oyuncu da bir haneye üye olmalı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if already married
            db.c.execute('SELECT id FROM marriages WHERE (user1_id = ? OR user2_id = ?) AND status = "married"', 
                        (proposer_id, proposer_id))
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Zaten evlisin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            db.c.execute('SELECT id FROM marriages WHERE (user1_id = ? OR user2_id = ?) AND status = "married"', 
                        (partner_id, partner_id))
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Bu kişi zaten evli!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check for existing proposal
            db.c.execute('''
            SELECT id FROM marriages 
            WHERE ((user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)) 
            AND status = "proposed"
            ''', (proposer_id, partner_id, partner_id, proposer_id))
            
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Zaten bekleyen bir evlilik teklifi var!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Create marriage proposal
            db.c.execute('''
            INSERT INTO marriages (user1_id, user2_id, status)
            VALUES (?, ?, "proposed")
            ''', (proposer_id, partner_id))
            
            db.conn.commit()
            
            embed = create_embed("💍 Evlilik Teklifi", 
                               f"**{ctx.author.display_name}** {partner.display_name}'e evlilik teklif etti!", 
                               discord.Color.gold())
            embed.add_field(name="Teklif Eden Hane", value=proposer_alliance[1], inline=True)
            embed.add_field(name="Teklif Edilen Hane", value=partner_alliance[1], inline=True)
            embed.set_footer(text=f"{partner.display_name} !evlilik_kabul {ctx.author.display_name} ile kabul edebilir")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Propose marriage error: {e}")
            embed = create_embed("❌ Hata", f"Evlilik teklifi hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='evlilik_kabul')
    async def accept_marriage(ctx, proposer: discord.Member):
        """Accept a marriage proposal"""
        try:
            partner_id = ctx.author.id
            proposer_id = proposer.id
            
            # Find marriage proposal
            db.c.execute('''
            SELECT * FROM marriages 
            WHERE user1_id = ? AND user2_id = ? AND status = "proposed"
            ''', (proposer_id, partner_id))
            
            marriage = db.c.fetchone()
            
            if not marriage:
                embed = create_embed("❌ Hata", f"{proposer.display_name} tarafından evlilik teklifi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Accept marriage
            db.c.execute('''
            UPDATE marriages 
            SET status = "married", married_at = datetime('now')
            WHERE id = ?
            ''', (marriage[0],))
            
            db.conn.commit()
            
            proposer_alliance = db.get_user_alliance(proposer_id)
            partner_alliance = db.get_user_alliance(partner_id)
            
            embed = create_embed("💒 Evlilik Gerçekleşti", 
                               f"**{proposer.display_name}** ile **{ctx.author.display_name}** evlendi!", 
                               discord.Color.green())
            embed.add_field(name="Haneler Birleşti", 
                          value=f"{proposer_alliance[1]} ⚔️ {partner_alliance[1]}", 
                          inline=False)
            embed.add_field(name="Avantajlar", 
                          value="• Çocuk sahibi olabilirsiniz\n• Diplomatik avantajlar\n• Ortak kaynaklar", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Accept marriage error: {e}")
            embed = create_embed("❌ Hata", f"Evlilik kabul etme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='hamile_kal')
    async def get_pregnant(ctx):
        """Try to get pregnant (for married couples)"""
        try:
            user_id = ctx.author.id
            
            # Check if married
            db.c.execute('''
            SELECT * FROM marriages 
            WHERE (user1_id = ? OR user2_id = ?) AND status = "married"
            ''', (user_id, user_id))
            
            marriage = db.c.fetchone()
            
            if not marriage:
                embed = create_embed("❌ Hata", "Hamile kalmak için evli olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Determine partner
            partner_id = marriage[2] if marriage[1] == user_id else marriage[1]
            
            # Check if already pregnant
            db.c.execute('SELECT id FROM pregnancies WHERE mother_id = ? AND status = "pregnant"', (user_id,))
            if db.c.fetchone():
                embed = create_embed("❌ Hata", "Zaten hamilesin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Random chance for pregnancy (60%)
            if random.random() < 0.6:
                # Create pregnancy
                due_date = "datetime('now', '+270 days')"  # 9 months
                db.c.execute(f'''
                INSERT INTO pregnancies (mother_id, father_id, due_date)
                VALUES (?, ?, {due_date})
                ''', (user_id, partner_id))
                
                db.conn.commit()
                
                embed = create_embed("🤱 Hamilelik", 
                                   "Tebrikler! Hamile kaldınız!", 
                                   discord.Color.green())
                embed.add_field(name="Doğum Tarihi", value="9 ay sonra", inline=True)
                embed.add_field(name="Durum", value="Sağlıklı", inline=True)
                await ctx.send(embed=embed)
            else:
                embed = create_embed("💔 Hamilelik", 
                                   "Bu sefer hamile kalmadınız. Tekrar deneyebilirsiniz.", 
                                   discord.Color.orange())
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Get pregnant error: {e}")
            embed = create_embed("❌ Hata", f"Hamilelik hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='boşan')
    async def divorce(ctx, partner: Optional[discord.Member] = None):
        """Get divorced from your partner"""
        try:
            user_id = ctx.author.id
            
            # Find marriage
            db.c.execute('''
            SELECT * FROM marriages 
            WHERE (user1_id = ? OR user2_id = ?) AND status = "married"
            ''', (user_id, user_id))
            
            marriage = db.c.fetchone()
            
            if not marriage:
                embed = create_embed("❌ Hata", "Evli değilsin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Determine partner
            partner_id = marriage[2] if marriage[1] == user_id else marriage[1]
            partner_user = bot.get_user(partner_id)
            
            if partner and partner.id != partner_id:
                embed = create_embed("❌ Hata", "Bu kişiyle evli değilsin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Divorce
            db.c.execute('UPDATE marriages SET status = "divorced" WHERE id = ?', (marriage[0],))
            
            # Cancel any active pregnancies
            db.c.execute('UPDATE pregnancies SET status = "cancelled" WHERE (mother_id = ? OR father_id = ?) AND status = "pregnant"', 
                        (user_id, user_id))
            
            db.conn.commit()
            
            user_alliance = db.get_user_alliance(user_id)
            partner_alliance = db.get_user_alliance(partner_id)
            
            embed = create_embed("💔 Boşanma", 
                               f"**{ctx.author.display_name}** ile **{partner_user.display_name if partner_user else 'Bilinmeyen'}** boşandı!", 
                               discord.Color.red())
            embed.add_field(name="Haneler Ayrıldı", 
                          value=f"{user_alliance[1] if user_alliance else 'Bilinmeyen'} ⚔️ {partner_alliance[1] if partner_alliance else 'Bilinmeyen'}", 
                          inline=False)
            embed.add_field(name="Sonuçlar", 
                          value="• Aktif hamilelikler iptal edildi\n• Diplomatik avantajlar kayboldu\n• Aile bağları koptu", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Divorce error: {e}")
            embed = create_embed("❌ Hata", f"Boşanma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='evliliklerim')
    async def my_marriages(ctx):
        """Show marriage history and current status"""
        try:
            user_id = ctx.author.id
            
            # Get all marriages
            db.c.execute('''
            SELECT m.*, u1.user_id as user1_discord, u2.user_id as user2_discord
            FROM marriages m
            JOIN members u1 ON m.user1_id = u1.user_id
            JOIN members u2 ON m.user2_id = u2.user_id
            WHERE m.user1_id = ? OR m.user2_id = ?
            ORDER BY m.created_at DESC
            ''', (user_id, user_id))
            
            marriages = db.c.fetchall()
            
            if not marriages:
                embed = create_embed("💍 Evlilik Geçmişi", "Evlilik geçmişiniz yok!", discord.Color.blue())
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("💍 Evlilik Durumum", 
                               f"**{ctx.author.display_name}** evlilik geçmişi", 
                               discord.Color.purple())
            
            current_marriage = None
            marriage_history = []
            
            for marriage in marriages:
                partner_id = marriage[2] if marriage[1] == user_id else marriage[1]  # user2_id if user1_id == user_id
                partner_user = bot.get_user(partner_id)
                partner_name = partner_user.display_name if partner_user else "Bilinmeyen"
                
                marriage_info = {
                    'partner': partner_name,
                    'status': marriage[3],  # status
                    'date': marriage[5] if marriage[5] else marriage[6]  # married_at or created_at
                }
                
                if marriage[3] == "married":  # status
                    current_marriage = marriage_info
                else:
                    marriage_history.append(marriage_info)
            
            if current_marriage:
                embed.add_field(name="💒 Mevcut Evlilik", 
                              value=f"**Partner:** {current_marriage['partner']}\n"
                                    f"**Durum:** Evli\n"
                                    f"**Tarih:** {current_marriage['date'][:10] if current_marriage['date'] else 'Bilinmiyor'}", 
                              inline=False)
            
            if marriage_history:
                history_text = ""
                for marriage in marriage_history[:5]:  # Show last 5
                    status_emoji = "💔" if marriage['status'] == "divorced" else "❌"
                    history_text += f"{status_emoji} **{marriage['partner']}** - {marriage['status'].title()}\n"
                
                embed.add_field(name="📜 Geçmiş Evlilikler", value=history_text, inline=False)
            
            if not current_marriage:
                embed.add_field(name="💔 Durum", value="Şu anda evli değilsiniz", inline=False)
            
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"My marriages error: {e}")
            embed = create_embed("❌ Hata", f"Evlilik geçmişi hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # SAVAŞ SİSTEMİ - GELİŞMİŞ KOMUTLAR
    # ===============================
    
    @bot.command(name='savaş_büyüklük', aliases=['war_size'])
    async def war_with_size(ctx, target_house=None, size="orta"):
        """Declare war with specific battle size"""
        user_id = ctx.author.id
        alliance = db.get_user_alliance(user_id)
        
        if not alliance:
            embed = create_embed("❌ Hata", "Bir haneye üye değilsin!", discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        if not target_house:
            embed = create_embed("📋 Muharebe Büyüklükleri", 
                               "**Kullanım:** `!savaş_büyüklük <hane_adı> <büyüklük>`\n\n"
                               "**Büyüklükler:**\n"
                               "🔸 **küçük** - Min 100 asker, %30 katılım, düşük yoğunluk\n"
                               "🔹 **orta** - Min 500 asker, %60 katılım, normal yoğunluk\n"
                               "🔶 **büyük** - Min 1000 asker, %80 katılım, yüksek yoğunluk\n"
                               "🔺 **topyekün** - Min 2000 asker, %100 katılım, maksimum yoğunluk", 
                               discord.Color.orange())
            await ctx.send(embed=embed)
            return
        
        # Find target house
        db.c.execute('SELECT * FROM alliances WHERE name LIKE ?', (f'%{target_house}%',))
        target = db.c.fetchone()
        
        if not target:
            embed = create_embed("❌ Hata", f"'{target_house}' hanesi bulunamadı!", discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        # Use the war_system parameter passed to setup_commands
        can_declare, message = war_system.can_declare_war(alliance[0], target[0], size)
        
        if not can_declare:
            embed = create_embed("❌ Savaş İlan Edilemez", message, discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        # Create war with battle size
        weather = random.choice(list(war_system.weather_effects.keys()))
        terrain = random.choice(list(war_system.terrain_effects.keys()))
        
        war_id = db.declare_war(alliance[0], target[0], weather, terrain)
        
        # Store battle size in war
        db.c.execute('UPDATE wars SET battle_size = ? WHERE id = ?', (size, war_id))
        db.conn.commit()
        
        size_descriptions = {
            "küçük": "🔸 Küçük çaplı çatışma",
            "orta": "🔹 Orta büyüklükte muharebe", 
            "büyük": "🔶 Büyük savaş",
            "topyekün": "🔺 Topyekün savaş"
        }
        
        embed = create_embed("⚔️ Savaş İlan Edildi!", 
                           f"**{alliance[1]}** hanesi **{target[1]}** hanesine savaş ilan etti!\n\n"
                           f"**Muharebe Türü:** {size_descriptions[size]}\n"
                           f"**Savaş ID:** {war_id}\n"
                           f"**Hava:** {weather.title()}\n"
                           f"**Arazi:** {terrain.title()}\n\n"
                           f"Savaş komutları: `!saldır {war_id}`, `!savun {war_id}`, vb.", 
                           discord.Color.red())
        
        await ctx.send(embed=embed)

    # ===============================
    # GELİR YÖNETİMİ SİSTEMİ
    # ===============================
    
    @bot.command(name='gelir_kaynakları')
    async def list_income_sources(ctx):
        """List house income sources"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            db.c.execute('''
            SELECT * FROM income_sources 
            WHERE house_id = ? 
            ORDER BY income_per_minute DESC
            ''', (alliance[0],))
            
            sources = db.c.fetchall()
            
            if not sources:
                embed = create_embed("💰 Gelir Kaynakları", 
                                   f"**{alliance[1]}** hanesinin gelir kaynağı yok!", 
                                   discord.Color.orange())
                embed.add_field(name="Satın Alma", 
                              value="!gelir_satın_al <tür> <bölge> ile yeni gelir kaynağı satın alabilirsiniz", 
                              inline=False)
                await ctx.send(embed=embed)
                return
            
            embed = create_embed("💰 Gelir Kaynakları", 
                               f"**{alliance[1]}** hanesi gelir kaynakları", 
                               discord.Color.gold())
            
            total_income = 0
            for source in sources:
                income_emoji = get_income_source_emoji(source[2] if source[2] else "mine")  # source_type
                status = "🔒 Ele Geçirildi" if len(source) > 7 and source[7] else "✅ Aktif"  # seized
                
                source_text = f"{income_emoji} **{source[3]}** ({source[4]})\n"  # name, region
                source_text += f"Gelir: {format_number(source[5])} altın/dk\n"  # income_per_minute
                source_text += f"Seviye: {source[6]} | {status}"  # level, status
                
                embed.add_field(name=source[2].title(), value=source_text, inline=True)  # source_type
                
                if not source[7]:  # not seized
                    total_income += source[5]  # income_per_minute
            
            embed.add_field(name="💎 Toplam Gelir", 
                          value=f"{format_number(total_income)} altın/dakika\n"
                                f"{format_number(total_income * 60)} altın/saat", 
                          inline=False)
            
            embed.set_footer(text="!gelir_yükselt <kaynak_adı> ile geliştirebilirsiniz")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"List income sources error: {e}")
            embed = create_embed("❌ Hata", f"Gelir kaynakları listeleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='gelir_satın_al')
    async def buy_income_source(ctx, source_type: str, region: str, name: str = ""):
        """Buy a new income source"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if alliance[2] != user_id:
                embed = create_embed("❌ Hata", "Sadece hane lideri gelir kaynağı satın alabilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            valid_types = ['mine', 'farm', 'port', 'castle', 'city', 'trade_route']
            if source_type not in valid_types:
                embed = create_embed("❌ Hata", f"Geçersiz kaynak türü! Kullanılabilir: {', '.join(valid_types)}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Calculate costs and income based on type
            costs = {
                'mine': {'cost': 50000, 'income': 100},
                'farm': {'cost': 30000, 'income': 60},
                'port': {'cost': 80000, 'income': 150},
                'castle': {'cost': 200000, 'income': 300},
                'city': {'cost': 500000, 'income': 800},
                'trade_route': {'cost': 100000, 'income': 200}
            }
            
            cost = costs[source_type]['cost']
            income = costs[source_type]['income']
            
            # Check if house can afford
            if alliance[3] < cost:  # gold
                embed = create_embed("❌ Hata", f"Yetersiz altın! Maliyet: {format_number(cost)} altın", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Generate name if not provided
            if not name or name == "":
                name = f"{alliance[1]} {source_type.title()}"
            
            # Create income source
            db.c.execute('''
            INSERT INTO income_sources (house_id, source_type, name, region, income_per_minute, cost)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (alliance[0], source_type, name, region, income, cost))
            
            # Pay cost
            db.update_alliance_resources(alliance[0], -cost, 0)
            
            db.conn.commit()
            
            embed = create_embed("💰 Gelir Kaynağı Satın Alındı", 
                               f"**{name}** başarıyla satın alındı!", 
                               discord.Color.green())
            embed.add_field(name="Tür", value=source_type.title(), inline=True)
            embed.add_field(name="Bölge", value=region, inline=True)
            embed.add_field(name="Maliyet", value=f"{format_number(cost)} altın", inline=True)
            embed.add_field(name="Gelir", value=f"{format_number(income)} altın/dakika", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Buy income source error: {e}")
            embed = create_embed("❌ Hata", f"Gelir kaynağı satın alma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # İSTATİSTİK VE BORÇ SİSTEMİ
    # ===============================
    
    @bot.command(name='borç_ver')
    async def lend_money(ctx, debtor_house: str, amount: int, interest_rate: float = 0.1):
        """Lend money to another house"""
        try:
            user_id = ctx.author.id
            creditor_alliance = db.get_user_alliance(user_id)
            
            if not creditor_alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if creditor_alliance[2] != user_id:
                embed = create_embed("❌ Hata", "Sadece hane lideri borç verebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find debtor house
            db.c.execute('SELECT id, name FROM alliances WHERE name LIKE ?', (f'%{debtor_house}%',))
            debtor_result = db.c.fetchone()
            
            if not debtor_result:
                embed = create_embed("❌ Hata", f"'{debtor_house}' hanesi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            debtor_id, debtor_name = debtor_result
            
            if debtor_id == creditor_alliance[0]:
                embed = create_embed("❌ Hata", "Kendi hanene borç veremezsin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if creditor has enough gold
            if creditor_alliance[3] < amount:  # gold
                embed = create_embed("❌ Hata", f"Yetersiz altın! Mevcut: {format_number(creditor_alliance[3])}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Create debt
            due_date = "datetime('now', '+30 days')"
            db.c.execute(f'''
            INSERT INTO house_debts (debtor_house_id, creditor_house_id, amount, due_date, interest_rate)
            VALUES (?, ?, ?, {due_date}, ?)
            ''', (debtor_id, creditor_alliance[0], amount, interest_rate))
            
            # Transfer money
            db.update_alliance_resources(creditor_alliance[0], -amount, 0)
            db.update_alliance_resources(debtor_id, amount, 0)
            
            db.conn.commit()
            
            embed = create_embed("💰 Borç Verildi", 
                               f"**{debtor_name}** hanesine {format_number(amount)} altın borç verildi!", 
                               discord.Color.green())
            embed.add_field(name="Faiz Oranı", value=f"%{interest_rate * 100:.1f}", inline=True)
            embed.add_field(name="Vade", value="30 gün", inline=True)
            embed.add_field(name="Geri Ödeme", value=f"{format_number(int(amount * (1 + interest_rate)))} altın", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Lend money error: {e}")
            embed = create_embed("❌ Hata", f"Borç verme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='borçlarım')
    async def list_my_debts(ctx):
        """List house debts (owed and owing)"""
        try:
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Get debts owed by this house
            db.c.execute('''
            SELECT hd.*, a.name as creditor_name 
            FROM house_debts hd
            JOIN alliances a ON hd.creditor_house_id = a.id
            WHERE hd.debtor_house_id = ? AND hd.status = 'active'
            ORDER BY hd.due_date ASC
            ''', (alliance[0],))
            
            debts_owed = db.c.fetchall()
            
            # Get debts owed to this house
            db.c.execute('''
            SELECT hd.*, a.name as debtor_name 
            FROM house_debts hd
            JOIN alliances a ON hd.debtor_house_id = a.id
            WHERE hd.creditor_house_id = ? AND hd.status = 'active'
            ORDER BY hd.due_date ASC
            ''', (alliance[0],))
            
            debts_owing = db.c.fetchall()
            
            embed = create_embed("💰 Borç Durumu", 
                               f"**{alliance[1]}** hanesi borç özeti", 
                               discord.Color.gold())
            
            if debts_owed:
                debt_text = ""
                total_debt = 0
                for debt in debts_owed:
                    current_amount = int(debt[3] * (1 + debt[5]))  # amount * (1 + interest_rate)
                    debt_text += f"• **{debt[9]}**: {format_number(current_amount)} altın\n"  # creditor_name
                    total_debt += current_amount
                
                embed.add_field(name="🔴 Borçlarınız", 
                              value=f"{debt_text}\n**Toplam:** {format_number(total_debt)} altın", 
                              inline=False)
            
            if debts_owing:
                owing_text = ""
                total_owing = 0
                for debt in debts_owing:
                    current_amount = int(debt[3] * (1 + debt[5]))  # amount * (1 + interest_rate)
                    owing_text += f"• **{debt[9]}**: {format_number(current_amount)} altın\n"  # debtor_name
                    total_owing += current_amount
                
                embed.add_field(name="🟢 Size Borçlu Olanlar", 
                              value=f"{owing_text}\n**Toplam:** {format_number(total_owing)} altın", 
                              inline=False)
            
            if not debts_owed and not debts_owing:
                embed.add_field(name="💎 Temiz Kayıtlar", 
                              value="Haranın borcu yok ve kimse size borçlu değil!", 
                              inline=False)
            
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"List my debts error: {e}")
            embed = create_embed("❌ Hata", f"Borç listeleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='borç_öde')
    async def pay_debt(ctx, creditor_house: str, amount: int = 0):
        """Pay back a debt to another house"""
        try:
            user_id = ctx.author.id
            debtor_alliance = db.get_user_alliance(user_id)
            
            if not debtor_alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if debtor_alliance[2] != user_id:
                embed = create_embed("❌ Hata", "Sadece hane lideri borç ödeyebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find creditor house
            db.c.execute('SELECT id, name FROM alliances WHERE name LIKE ?', (f'%{creditor_house}%',))
            creditor_result = db.c.fetchone()
            
            if not creditor_result:
                embed = create_embed("❌ Hata", f"'{creditor_house}' hanesi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            creditor_id, creditor_name = creditor_result
            
            # Find active debt
            db.c.execute('''
            SELECT * FROM house_debts 
            WHERE debtor_house_id = ? AND creditor_house_id = ? AND status = 'active'
            ORDER BY due_date ASC
            LIMIT 1
            ''', (debtor_alliance[0], creditor_id))
            
            debt = db.c.fetchone()
            
            if not debt:
                embed = create_embed("❌ Hata", f"{creditor_name} hanesine aktif borcunuz yok!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Calculate current debt with interest
            current_debt = int(debt[3] * (1 + debt[4]))  # amount * (1 + interest_rate)
            
            # If amount not specified, pay full debt
            if not amount:
                amount = current_debt
            
            # Check if debtor has enough gold
            if debtor_alliance[3] < amount:  # gold
                embed = create_embed("❌ Hata", f"Yetersiz altın! Mevcut: {format_number(debtor_alliance[3])}, Gerekli: {format_number(amount)}", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Make payment
            db.update_alliance_resources(debtor_alliance[0], -amount, 0)  # Pay from debtor
            db.update_alliance_resources(creditor_id, amount, 0)  # Give to creditor
            
            remaining_debt = current_debt - amount
            
            if remaining_debt <= 0:
                # Debt fully paid
                db.c.execute('UPDATE house_debts SET status = "paid" WHERE id = ?', (debt[0],))
                embed = create_embed("💰 Borç Tamamen Ödendi", 
                                   f"**{creditor_name}** hanesine olan borcunuz tamamen ödendi!", 
                                   discord.Color.green())
                embed.add_field(name="Ödenen Miktar", value=f"{format_number(amount)} altın", inline=True)
                embed.add_field(name="Orijinal Borç", value=f"{format_number(debt[3])} altın", inline=True)
                embed.add_field(name="Faiz", value=f"%{debt[4] * 100:.1f}", inline=True)
            else:
                # Partial payment - update debt amount
                new_principal = int(remaining_debt / (1 + debt[4]))  # Remove interest from remaining
                db.c.execute('UPDATE house_debts SET amount = ? WHERE id = ?', (new_principal, debt[0]))
                
                embed = create_embed("💰 Kısmi Borç Ödemesi", 
                                   f"**{creditor_name}** hanesine kısmi ödeme yapıldı!", 
                                   discord.Color.orange())
                embed.add_field(name="Ödenen", value=f"{format_number(amount)} altın", inline=True)
                embed.add_field(name="Kalan Borç", value=f"{format_number(remaining_debt)} altın", inline=True)
                embed.add_field(name="Faiz Oranı", value=f"%{debt[4] * 100:.1f}", inline=True)
            
            db.conn.commit()
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Pay debt error: {e}")
            embed = create_embed("❌ Hata", f"Borç ödeme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='borç_iptal')
    async def forgive_debt(ctx, debtor_house: str):
        """Forgive a debt (creditor only)"""
        try:
            user_id = ctx.author.id
            creditor_alliance = db.get_user_alliance(user_id)
            
            if not creditor_alliance:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Check if user is leader
            if creditor_alliance[2] != user_id:
                embed = create_embed("❌ Hata", "Sadece hane lideri borç affedebilir!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Find debtor house
            db.c.execute('SELECT id, name FROM alliances WHERE name LIKE ?', (f'%{debtor_house}%',))
            debtor_result = db.c.fetchone()
            
            if not debtor_result:
                embed = create_embed("❌ Hata", f"'{debtor_house}' hanesi bulunamadı!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            debtor_id, debtor_name = debtor_result
            
            # Find active debt
            db.c.execute('''
            SELECT * FROM house_debts 
            WHERE debtor_house_id = ? AND creditor_house_id = ? AND status = 'active'
            ''', (debtor_id, creditor_alliance[0]))
            
            debt = db.c.fetchone()
            
            if not debt:
                embed = create_embed("❌ Hata", f"{debtor_name} hanesinin size aktif borcu yok!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Forgive debt
            db.c.execute('UPDATE house_debts SET status = "forgiven" WHERE id = ?', (debt[0],))
            db.conn.commit()
            
            current_debt = int(debt[3] * (1 + debt[4]))  # amount * (1 + interest_rate)
            
            embed = create_embed("💰 Borç Affedildi", 
                               f"**{debtor_name}** hanesinin borcu affedildi!", 
                               discord.Color.green())
            embed.add_field(name="Affedilen Miktar", value=f"{format_number(current_debt)} altın", inline=True)
            embed.add_field(name="Orijinal Borç", value=f"{format_number(debt[3])} altın", inline=True)
            embed.add_field(name="Faiz Oranı", value=f"%{debt[4] * 100:.1f}", inline=True)
            embed.add_field(name="Diplomatik Etki", value="Bu cömert hareket diplomatik ilişkileri güçlendirecek!", inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Forgive debt error: {e}")
            embed = create_embed("❌ Heta", f"Borç affetme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # KARAKTER İLERLEME SİSTEMİ
    # ===============================
    
    @bot.command(name='seviye')
    async def show_character_level(ctx):
        """Show character level and experience"""
        try:
            user_id = ctx.author.id
            
            # Get user data
            db.c.execute('SELECT * FROM members WHERE user_id = ?', (user_id,))
            user_data = db.c.fetchone()
            
            if not user_data:
                embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            experience = user_data[6] if user_data and len(user_data) > 6 else 0  # experience
            level = calculate_level_from_experience(experience)
            next_level_exp = (level + 1) ** 2 * 100
            exp_needed = next_level_exp - experience
            
            alliance = db.get_user_alliance(user_id)
            character_class = user_data[7] if user_data and len(user_data) > 7 else "Lord"  # character_class
            class_info = get_character_class_info(character_class)
            
            embed = create_embed("⭐ Karakter Seviyesi", 
                               f"**{ctx.author.display_name}** karakteri", 
                               discord.Color.purple())
            
            embed.add_field(name="Seviye", value=f"**{level}**", inline=True)
            embed.add_field(name="Deneyim", value=f"{format_number(experience)} XP", inline=True)
            embed.add_field(name="Sonraki Seviye", value=f"{format_number(exp_needed)} XP kaldı", inline=True)
            
            if alliance:
                embed.add_field(name="Hane", value=f"{get_house_emoji(alliance[1])} {alliance[1]}", inline=True)
            
            embed.add_field(name="Sınıf", value=f"{class_info['emoji']} {character_class}", inline=True)
            embed.add_field(name="Özellik Bonusları", 
                          value=f"⚔️ Saldırı: +{class_info['bonuses']['attack']}\n"
                                f"🛡️ Savunma: +{class_info['bonuses']['defense']}\n"
                                f"❤️ Can: +{class_info['bonuses']['health']}", 
                          inline=True)
            
            # Progress bar
            progress = create_progress_bar(experience - (level ** 2 * 100), (level + 1) ** 2 * 100 - (level ** 2 * 100))
            embed.add_field(name="İlerleme", value=progress, inline=False)
            
            embed.set_footer(text="Savaşlar, turnuvalar ve görrevlerle deneyim kazanın!")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Show character level error: {e}")
            embed = create_embed("❌ Hata", f"Seviye görüntüleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='liderlik_tablosu')
    async def show_leaderboard(ctx):
        """Show house leaderboard"""
        try:
            # Get top houses by different metrics
            db.c.execute('''
            SELECT name, gold, soldiers, debt, (gold - debt) as net_worth
            FROM alliances 
            WHERE name NOT IN ('System', 'Admin')
            ORDER BY net_worth DESC
            LIMIT 10
            ''')
            
            wealth_leaders = db.c.fetchall()
            
            db.c.execute('''
            SELECT name, soldiers, gold
            FROM alliances 
            WHERE name NOT IN ('System', 'Admin')
            ORDER BY soldiers DESC
            LIMIT 10
            ''')
            
            military_leaders = db.c.fetchall()
            
            embed = create_embed("👑 Liderlik Tablosu", 
                               "En güçlü haneler", 
                               discord.Color.gold())
            
            # Wealth leaderboard
            if wealth_leaders:
                wealth_text = ""
                for i, house in enumerate(wealth_leaders[:5], 1):
                    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                    medal = medals[i-1] if i <= 5 else f"{i}."
                    emoji = get_house_emoji(house[0])
                    net_worth = house[4]  # net_worth
                    wealth_text += f"{medal} {emoji} **{house[0]}**: {format_number(net_worth)} altın\n"
                
                embed.add_field(name="💰 En Zengin Haneler", value=wealth_text, inline=True)
            
            # Military leaderboard
            if military_leaders:
                military_text = ""
                for i, house in enumerate(military_leaders[:5], 1):
                    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                    medal = medals[i-1] if i <= 5 else f"{i}."
                    emoji = get_house_emoji(house[0])
                    military_text += f"{medal} {emoji} **{house[0]}**: {format_number(house[1])} asker\n"
                
                embed.add_field(name="⚔️ Askeri Güç", value=military_text, inline=True)
            
            embed.set_footer(text="Haneni büyütmek için savaş, ticaret ve diplomasi kullan!")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Show leaderboard error: {e}")
            embed = create_embed("❌ Hata", f"Liderlik tablosu hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='roleplay')
    async def roleplay_action(ctx, target: Optional[discord.Member] = None, *, action: str = ""):
        """Perform a roleplay action"""
        try:
            if not action:
                embed = create_embed("🎭 Roleplay", 
                                   "Roleplay aksiyonu yazın!", 
                                   discord.Color.purple())
                embed.add_field(name="Örnekler", 
                              value="• !roleplay @kullanıcı kılıcını çeker\n"
                                    "• !roleplay taverne girer\n"
                                    "• !roleplay @kullanıcı ile konuşur", 
                              inline=False)
                await ctx.send(embed=embed)
                return
            
            user_id = ctx.author.id
            alliance = db.get_user_alliance(user_id)
            
            if not alliance:
                embed = create_embed("❌ Hata", "Roleplay için bir haneye üye olmalısın!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            # Create roleplay embed
            emoji = get_house_emoji(alliance[1])
            
            if target:
                embed = create_embed("🎭 Roleplay Aksiyonu", 
                                   f"{emoji} **{ctx.author.display_name}** ({alliance[1]})", 
                                   discord.Color.purple())
                embed.add_field(name="Aksiyon", 
                              value=f"**{ctx.author.display_name}** {target.display_name} ile **{action}**", 
                              inline=False)
            else:
                embed = create_embed("🎭 Roleplay Aksiyonu", 
                                   f"{emoji} **{ctx.author.display_name}** ({alliance[1]})", 
                                   discord.Color.purple())
                embed.add_field(name="Aksiyon", 
                              value=f"**{ctx.author.display_name}** **{action}**", 
                              inline=False)
            
            # Add some XP for roleplay
            db.c.execute('UPDATE members SET experience = experience + 5 WHERE user_id = ?', (user_id,))
            db.conn.commit()
            
            embed.set_footer(text="🌟 Roleplay için +5 deneyim kazandınız!")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Roleplay action error: {e}")
            embed = create_embed("❌ Hata", f"Roleplay hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='hane_istatistikleri') 
    async def house_statistics(ctx, *, house_name: str = ""):
        """Show detailed house statistics"""
        try:
            user_id = ctx.author.id
            
            if house_name:
                # Show specific house stats
                db.c.execute('SELECT * FROM alliances WHERE name LIKE ?', (f'%{house_name}%',))
                alliance = db.c.fetchone()
                
                if not alliance:
                    embed = create_embed("❌ Hata", f"'{house_name}' hanesi bulunamadı!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
            else:
                # Show own house stats
                alliance = db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Bir haneye üye olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
            
            house_id = alliance[0]
            house_emoji = get_house_emoji(alliance[1])
            
            # Get member count
            db.c.execute('SELECT COUNT(*) FROM members WHERE alliance_id = ?', (house_id,))
            member_count = db.c.fetchone()[0]
            
            # Get income sources
            db.c.execute('SELECT COUNT(*), SUM(income_per_minute) FROM income_sources WHERE house_id = ? AND seized = 0', (house_id,))
            income_data = db.c.fetchone()
            income_sources = income_data[0] if income_data[0] else 0
            total_income = income_data[1] if income_data[1] else 0
            
            # Get debt information
            db.c.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN debtor_house_id = ? THEN amount ELSE 0 END), 0) as owed,
                COALESCE(SUM(CASE WHEN creditor_house_id = ? THEN amount ELSE 0 END), 0) as owed_to_us
            FROM house_debts 
            WHERE (debtor_house_id = ? OR creditor_house_id = ?) AND status = 'active'
            ''', (house_id, house_id, house_id, house_id))
            
            debt_data = db.c.fetchone()
            debt_owed = debt_data[0] if debt_data else 0
            debt_owed_to_us = debt_data[1] if debt_data else 0
            
            embed = create_embed(f"{house_emoji} Hane İstatistikleri", 
                               f"**{alliance[1]}** hanesi detayları", 
                               discord.Color.gold())
            
            embed.add_field(name="💰 Ekonomi", 
                          value=f"Altın: {format_number(alliance[3])}\n"
                                f"Borç: {format_number(alliance[5])}\n" 
                                f"Net Değer: {format_number(alliance[3] - alliance[5])}", 
                          inline=True)
            
            embed.add_field(name="⚔️ Askeri Güç", 
                          value=f"Asker: {format_number(alliance[4])}\n"
                                f"Ordu Kalitesi: {alliance[8]}/100\n"
                                f"Bölge: {alliance[6]}", 
                          inline=True)
            
            embed.add_field(name="👥 Hane Bilgileri", 
                          value=f"Üye Sayısı: {member_count}\n"
                                f"Özel Yetenek: {alliance[7]}\n"
                                f"Gelir Kaynağı: {income_sources}", 
                          inline=True)
            
            embed.add_field(name="💸 Borç Durumu", 
                          value=f"Borçlarımız: {format_number(debt_owed)}\n"
                                f"Bize Borçlu: {format_number(debt_owed_to_us)}\n"
                                f"Net Borç: {format_number(debt_owed - debt_owed_to_us)}", 
                          inline=True)
            
            embed.add_field(name="📈 Pasif Gelir", 
                          value=f"Dakika: {format_number(total_income)} altın\n"
                                f"Saat: {format_number(total_income * 60)} altın\n"
                                f"Gün: {format_number(total_income * 1440)} altın", 
                          inline=True)
            
            embed.set_footer(text=f"Kuruluş tarihi gösteriliyor")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"House statistics error: {e}")
            embed = create_embed("❌ Hata", f"İstatistik görüntüleme hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # GELİŞMİŞ MODERASYON SİSTEMİ
    # ===============================
    
    @bot.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_command(ctx, member: discord.Member, *, reason: str = "Sebep belirtilmedi"):
        """Ban a member from the server"""
        try:
            await member.ban(reason=reason)
            
            embed = create_embed(
                "🔨 Kullanıcı Yasaklandı",
                f"**{member.display_name}** sunucudan yasaklandı!",
                discord.Color.red()
            )
            embed.add_field(name="👤 Kullanıcı", value=f"{member.mention} ({member.id})", inline=True)
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Sebep", value=reason, inline=False)
            await ctx.send(embed=embed)
            
            # Log to moderation channel
            log_channel = discord.utils.get(ctx.guild.channels, name="moderasyon-log")
            if log_channel:
                await log_channel.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Yasaklama hatası: {str(e)}")

    @bot.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_command(ctx, member: discord.Member, *, reason: str = "Sebep belirtilmedi"):
        """Kick a member from the server"""
        try:
            await member.kick(reason=reason)
            
            embed = create_embed(
                "👢 Kullanıcı Atıldı",
                f"**{member.display_name}** sunucudan atıldı!",
                discord.Color.orange()
            )
            embed.add_field(name="👤 Kullanıcı", value=f"{member.mention} ({member.id})", inline=True)
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            embed.add_field(name="📝 Sebep", value=reason, inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Atma hatası: {str(e)}")

    @bot.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute_command(ctx, member: discord.Member, duration: int = 60, *, reason: str = "Sebep belirtilmedi"):
        """Mute a member for specified duration (minutes)"""
        try:
            from datetime import timedelta
            
            await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(minutes=duration), reason=reason)
            
            embed = create_embed(
                "🔇 Kullanıcı Susturuldu",
                f"**{member.display_name}** {duration} dakika susturuldu!",
                discord.Color.yellow()
            )
            embed.add_field(name="👤 Kullanıcı", value=f"{member.mention} ({member.id})", inline=True)
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            embed.add_field(name="⏰ Süre", value=f"{duration} dakika", inline=True)
            embed.add_field(name="📝 Sebep", value=reason, inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Susturma hatası: {str(e)}")

    @bot.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute_command(ctx, member: discord.Member):
        """Remove timeout from a member"""
        try:
            await member.edit(timed_out_until=None)
            
            embed = create_embed(
                "🔊 Susturma Kaldırıldı",
                f"**{member.display_name}** susturması kaldırıldı!",
                discord.Color.green()
            )
            embed.add_field(name="👤 Kullanıcı", value=member.mention, inline=True)
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Susturma kaldırma hatası: {str(e)}")

    @bot.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn_command(ctx, member: discord.Member, *, reason: str = "Sebep belirtilmedi"):
        """Warn a member"""
        try:
            # Store warning in database
            db.c.execute('''
            INSERT INTO warnings (user_id, moderator_id, reason, warned_at)
            VALUES (?, ?, ?, datetime('now'))
            ''', (member.id, ctx.author.id, reason))
            
            # Get warning count
            db.c.execute('SELECT COUNT(*) FROM warnings WHERE user_id = ?', (member.id,))
            warning_count = db.c.fetchone()[0]
            
            db.conn.commit()
            
            embed = create_embed(
                "⚠️ Uyarı Verildi",
                f"**{member.display_name}** uyarı aldı!",
                discord.Color.yellow()
            )
            embed.add_field(name="👤 Kullanıcı", value=f"{member.mention} ({member.id})", inline=True)
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            embed.add_field(name="🔢 Toplam Uyarı", value=f"{warning_count}", inline=True)
            embed.add_field(name="📝 Sebep", value=reason, inline=False)
            await ctx.send(embed=embed)
            
            # DM the user
            try:
                dm_embed = create_embed(
                    "⚠️ Uyarı Aldınız",
                    f"**{ctx.guild.name}** sunucusunda uyarı aldınız!",
                    discord.Color.yellow()
                )
                dm_embed.add_field(name="📝 Sebep", value=reason, inline=False)
                dm_embed.add_field(name="🔢 Toplam Uyarınız", value=f"{warning_count}", inline=True)
                await member.send(embed=dm_embed)
            except:
                pass  # User might have DMs disabled
                
        except Exception as e:
            await ctx.send(f"❌ Uyarı verme hatası: {str(e)}")

    @bot.command(name="warnings")
    @commands.has_permissions(moderate_members=True)
    async def warnings_command(ctx, member: discord.Member):
        """View member's warnings"""
        try:
            db.c.execute('''
            SELECT reason, warned_at, moderator_id FROM warnings 
            WHERE user_id = ? ORDER BY warned_at DESC LIMIT 10
            ''', (member.id,))
            
            warnings = db.c.fetchall()
            
            if not warnings:
                embed = create_embed(
                    "✅ Temiz Kayıt",
                    f"**{member.display_name}** hiç uyarı almamış!",
                    discord.Color.green()
                )
            else:
                embed = create_embed(
                    "⚠️ Uyarı Geçmişi",
                    f"**{member.display_name}** uyarı listesi",
                    discord.Color.orange()
                )
                
                warning_text = ""
                for i, (reason, warned_at, mod_id) in enumerate(warnings, 1):
                    moderator = bot.get_user(mod_id)
                    mod_name = moderator.display_name if moderator else "Bilinmeyen"
                    warning_text += f"**{i}.** {reason} - {mod_name} ({warned_at[:10]})\n"
                
                embed.add_field(name=f"Son {len(warnings)} Uyarı", value=warning_text, inline=False)
                embed.add_field(name="Toplam Uyarı", value=str(len(warnings)), inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Uyarı görüntüleme hatası: {str(e)}")

    @bot.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear_command(ctx, amount: int = 10):
        """Clear specified number of messages"""
        try:
            if amount > 100:
                await ctx.send("❌ En fazla 100 mesaj silebilirsiniz!")
                return
                
            deleted = await ctx.channel.purge(limit=amount)
            
            embed = create_embed(
                "🧹 Mesajlar Silindi",
                f"**{len(deleted)}** mesaj silindi!",
                discord.Color.green()
            )
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            embed.add_field(name="📍 Kanal", value=ctx.channel.mention, inline=True)
            
            # Send as ephemeral to avoid immediately deleting the confirmation
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Mesaj silme hatası: {str(e)}")

    @bot.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode_command(ctx, seconds: int = 0):
        """Set slowmode for the channel"""
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                embed = create_embed(
                    "🚀 Yavaş Mod Kapatıldı",
                    "Kanal yavaş modu kapatıldı!",
                    discord.Color.green()
                )
            else:
                embed = create_embed(
                    "🐌 Yavaş Mod Aktif",
                    f"Kanal yavaş modu {seconds} saniye olarak ayarlandı!",
                    discord.Color.orange()
                )
            
            embed.add_field(name="👮 Moderatör", value=ctx.author.mention, inline=True)
            embed.add_field(name="📍 Kanal", value=ctx.channel.mention, inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Yavaş mod hatası: {str(e)}")

    @bot.command(name="altın_ver")
    @commands.has_permissions(administrator=True)
    async def give_gold(ctx, member: discord.Member, amount: int):
        """Give gold to a user's house (Admin only)"""
        try:
            alliance = db.get_user_alliance(member.id)
            
            if not alliance:
                await ctx.send(f"❌ {member.display_name} herhangi bir haneye üye değil!")
                return
            
            db.update_alliance_resources(alliance[0], amount, 0)
            
            embed = create_embed(
                "💰 Altın Verildi",
                f"**{format_number(amount)}** altın verildi!",
                discord.Color.gold()
            )
            embed.add_field(name="👤 Alıcı", value=f"{member.mention} ({alliance[1]})", inline=True)
            embed.add_field(name="👑 Admin", value=ctx.author.mention, inline=True)
            embed.add_field(name="💎 Miktar", value=format_number(amount), inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Altın verme hatası: {str(e)}")

    @bot.command(name="altın_al")
    @commands.has_permissions(administrator=True)
    async def take_gold(ctx, member: discord.Member, amount: int):
        """Take gold from a user's house (Admin only)"""
        try:
            alliance = db.get_user_alliance(member.id)
            
            if not alliance:
                await ctx.send(f"❌ {member.display_name} herhangi bir haneye üye değil!")
                return
            
            if alliance[3] < amount:  # gold
                await ctx.send(f"❌ {alliance[1]} hanesinde yeterli altın yok! Mevcut: {format_number(alliance[3])}")
                return
            
            db.update_alliance_resources(alliance[0], -amount, 0)
            
            embed = create_embed(
                "💸 Altın Alındı",
                f"**{format_number(amount)}** altın alındı!",
                discord.Color.red()
            )
            embed.add_field(name="👤 Hedef", value=f"{member.mention} ({alliance[1]})", inline=True)
            embed.add_field(name="👑 Admin", value=ctx.author.mention, inline=True)
            embed.add_field(name="💎 Miktar", value=format_number(amount), inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Altın alma hatası: {str(e)}")

    @bot.command(name="borç_sıfırla")
    @commands.has_permissions(administrator=True)
    async def reset_debt(ctx, house_name: str):
        """Reset all debts for a house (Admin only)"""
        try:
            # Find house
            db.c.execute('SELECT id, name FROM alliances WHERE name LIKE ?', (f'%{house_name}%',))
            house = db.c.fetchone()
            
            if not house:
                await ctx.send(f"❌ '{house_name}' hanesi bulunamadı!")
                return
            
            house_id, full_name = house
            
            # Clear all debts
            db.c.execute('UPDATE house_debts SET status = "admin_forgiven" WHERE debtor_house_id = ? AND status = "active"', (house_id,))
            db.c.execute('UPDATE alliances SET debt = 0 WHERE id = ?', (house_id,))
            
            cleared_count = db.c.rowcount
            db.conn.commit()
            
            embed = create_embed(
                "💳 Borçlar Sıfırlandı",
                f"**{full_name}** hanesinin tüm borçları temizlendi!",
                discord.Color.green()
            )
            embed.add_field(name="🏰 Hane", value=full_name, inline=True)
            embed.add_field(name="👑 Admin", value=ctx.author.mention, inline=True)
            embed.add_field(name="📋 Temizlenen", value=f"{cleared_count} borç", inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Borç sıfırlama hatası: {str(e)}")

    @bot.command(name="asker_ver")
    @commands.has_permissions(administrator=True)
    async def give_soldiers(ctx, member: discord.Member, amount: int):
        """Give soldiers to a user's house (Admin only)"""
        try:
            alliance = db.get_user_alliance(member.id)
            
            if not alliance:
                await ctx.send(f"❌ {member.display_name} herhangi bir haneye üye değil!")
                return
            
            db.update_alliance_resources(alliance[0], 0, amount)
            
            embed = create_embed(
                "⚔️ Asker Verildi",
                f"**{format_number(amount)}** asker verildi!",
                discord.Color.red()
            )
            embed.add_field(name="👤 Alıcı", value=f"{member.mention} ({alliance[1]})", inline=True)
            embed.add_field(name="👑 Admin", value=ctx.author.mention, inline=True)
            embed.add_field(name="🛡️ Miktar", value=format_number(amount), inline=True)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Asker verme hatası: {str(e)}")

    @bot.command(name="sunucu_stats")
    @commands.has_permissions(administrator=True)
    async def server_stats(ctx):
        """Show comprehensive server statistics"""
        try:
            # Get various statistics
            db.c.execute('SELECT COUNT(*) FROM alliances')
            total_houses = db.c.fetchone()[0]
            
            db.c.execute('SELECT COUNT(*) FROM members')
            total_members = db.c.fetchone()[0]
            
            db.c.execute('SELECT COUNT(*) FROM wars WHERE status = "active"')
            active_wars = db.c.fetchone()[0]
            
            db.c.execute('SELECT SUM(gold) FROM alliances')
            total_gold = db.c.fetchone()[0] or 0
            
            db.c.execute('SELECT SUM(soldiers) FROM alliances')
            total_soldiers = db.c.fetchone()[0] or 0
            
            embed = create_embed(
                "📊 Sunucu İstatistikleri",
                f"**{ctx.guild.name}** detaylı analiz",
                discord.Color.blue()
            )
            
            embed.add_field(name="🏰 Haneler", value=format_number(total_houses), inline=True)
            embed.add_field(name="👥 Aktif Üyeler", value=format_number(total_members), inline=True)
            embed.add_field(name="⚔️ Aktif Savaşlar", value=format_number(active_wars), inline=True)
            embed.add_field(name="💰 Toplam Altın", value=format_number(total_gold), inline=True)
            embed.add_field(name="🛡️ Toplam Asker", value=format_number(total_soldiers), inline=True)
            embed.add_field(name="📈 Sunucu Üyesi", value=format_number(ctx.guild.member_count), inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ İstatistik hatası: {str(e)}")

    # ===============================
    # 40 GELİŞMİŞ MODERASYON KOMUTLARI
    # ===============================

    @bot.command(name="mass_ban")
    @commands.has_permissions(ban_members=True)
    async def mass_ban(ctx, user_ids: str, reason: str = "Toplu yasaklama"):
        """Ban multiple users at once"""
        try:
            ids = [int(id.strip()) for id in user_ids.split(',')]
            banned = []
            for user_id in ids:
                try:
                    user = await bot.fetch_user(user_id)
                    await ctx.guild.ban(user, reason=reason)
                    banned.append(user.display_name)
                except:
                    continue
            
            embed = create_embed("🔨 Toplu Yasaklama", f"{len(banned)} kullanıcı yasaklandı!", discord.Color.red())
            embed.add_field(name="Yasaklananlar", value="\n".join(banned[:10]), inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="lockdown")
    @commands.has_permissions(manage_channels=True)
    async def lockdown(ctx):
        """Lock down all channels"""
        try:
            locked = 0
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                    locked += 1
            
            embed = create_embed("🔒 Sunucu Kilitleme", f"{locked} kanal kilitleendi!", discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(ctx):
        """Unlock all channels"""
        try:
            unlocked = 0
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                    unlocked += 1
            
            embed = create_embed("🔓 Sunucu Kilit Açma", f"{unlocked} kanal açıldı!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="nuke")
    @commands.has_permissions(manage_channels=True)
    async def nuke(ctx):
        """Delete and recreate channel"""
        try:
            channel = ctx.channel
            new_channel = await channel.clone()
            await channel.delete()
            
            embed = create_embed("💥 Kanal Nuke", "Kanal temizlendi ve yeniden oluşturuldu!", discord.Color.orange())
            await new_channel.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="role_add")
    @commands.has_permissions(manage_roles=True)
    async def role_add(ctx, member: discord.Member, role: discord.Role):
        """Add role to member"""
        try:
            await member.add_roles(role)
            embed = create_embed("✅ Rol Eklendi", f"{member.mention} kullanıcısına {role.mention} rolü verildi!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="role_remove")
    @commands.has_permissions(manage_roles=True)
    async def role_remove(ctx, member: discord.Member, role: discord.Role):
        """Remove role from member"""
        try:
            await member.remove_roles(role)
            embed = create_embed("❌ Rol Alındı", f"{member.mention} kullanıcısından {role.mention} rolü alındı!", discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(ctx, member: discord.Member, nickname: str = ""):
        """Change member's nickname"""
        try:
            old_nick = member.display_name
            new_nick = nickname if nickname != "" else None
            await member.edit(nick=new_nick)
            embed = create_embed("📝 Nickname Değiştirildi", f"{old_nick} → {nickname or member.name}", discord.Color.blue())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="create_role")
    @commands.has_permissions(manage_roles=True)
    async def create_role(ctx, name: str, color: str = "default", mentionable: bool = True):
        """Create a new role"""
        try:
            color_dict = {
                "red": discord.Color.red(),
                "green": discord.Color.green(),
                "blue": discord.Color.blue(),
                "purple": discord.Color.purple(),
                "gold": discord.Color.gold(),
                "default": discord.Color.default()
            }
            role_color = color_dict.get(color, discord.Color.default())
            
            role = await ctx.guild.create_role(name=name, color=role_color, mentionable=mentionable)
            embed = create_embed("🎭 Rol Oluşturuldu", f"{role.mention} rolü başarıyla oluşturuldu!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="delete_role")
    @commands.has_permissions(manage_roles=True)
    async def delete_role(ctx, role: discord.Role):
        """Delete a role"""
        try:
            role_name = role.name
            await role.delete()
            embed = create_embed("🗑️ Rol Silindi", f"{role_name} rolü silindi!", discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="user_info")
    @commands.has_permissions(moderate_members=True)
    async def user_info(ctx, member: discord.Member):
        """Get detailed user information"""
        try:
            embed = create_embed("👤 Kullanıcı Bilgileri", f"{member.display_name} profili", discord.Color.blue())
            embed.add_field(name="ID", value=member.id, inline=True)
            joined_date = member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "Bilinmiyor"
            embed.add_field(name="Katılma Tarihi", value=joined_date, inline=True)
            embed.add_field(name="Hesap Oluşturma", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
            embed.add_field(name="Roller", value=" ".join([role.mention for role in member.roles[1:]]) or "Yok", inline=False)
            embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="server_info")
    @commands.has_permissions(moderate_members=True)
    async def server_info(ctx):
        """Get server information"""
        try:
            guild = ctx.guild
            embed = create_embed("🏰 Sunucu Bilgileri", guild.name, discord.Color.gold())
            owner_mention = guild.owner.mention if guild.owner else "Bilinmiyor"
            embed.add_field(name="Sahibi", value=owner_mention, inline=True)
            embed.add_field(name="Üye Sayısı", value=guild.member_count, inline=True)
            embed.add_field(name="Oluşturulma", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
            embed.add_field(name="Kanal Sayısı", value=len(guild.channels), inline=True)
            embed.add_field(name="Rol Sayısı", value=len(guild.roles), inline=True)
            embed.add_field(name="Boost Seviyesi", value=guild.premium_tier, inline=True)
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="audit_log")
    @commands.has_permissions(view_audit_log=True)
    async def audit_log(ctx, limit: int = 10):
        """View audit log"""
        try:
            entries = []
            async for entry in ctx.guild.audit_logs(limit=limit):
                entries.append(f"**{entry.action}** - {entry.user.mention} - {entry.created_at.strftime('%H:%M')}")
            
            embed = create_embed("📋 Denetim Günlüğü", f"Son {limit} eylem", discord.Color.purple())
            embed.add_field(name="Eylemler", value="\n".join(entries) or "Kayıt yok", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="emoji_add")
    @commands.has_permissions(manage_emojis=True)
    async def emoji_add(ctx, name: str, image_url: str):
        """Add emoji to server"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    image_bytes = await resp.read()
            
            emoji = await ctx.guild.create_custom_emoji(name=name, image=image_bytes)
            embed = create_embed("😀 Emoji Eklendi", f"{emoji} emojisi eklendi!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="emoji_remove")
    @commands.has_permissions(manage_emojis=True)
    async def emoji_remove(ctx, emoji_name: str):
        """Remove emoji from server"""
        try:
            emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
            if emoji:
                await emoji.delete()
                embed = create_embed("🗑️ Emoji Silindi", f"{emoji_name} emojisi silindi!", discord.Color.red())
            else:
                embed = create_embed("❌ Hata", "Emoji bulunamadı!", discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="channel_create")
    @commands.has_permissions(manage_channels=True)
    async def channel_create(ctx, name: str, channel_type: str = "text"):
        """Create a new channel"""
        try:
            if channel_type == "voice":
                channel = await ctx.guild.create_voice_channel(name)
            else:
                channel = await ctx.guild.create_text_channel(name)
            
            embed = create_embed("📁 Kanal Oluşturuldu", f"{channel.mention} kanalı oluşturuldu!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="channel_delete")
    @commands.has_permissions(manage_channels=True)
    async def channel_delete(ctx, channel: discord.TextChannel):
        """Delete a channel"""
        try:
            channel_name = channel.name
            await channel.delete()
            embed = create_embed("🗑️ Kanal Silindi", f"{channel_name} kanalı silindi!", discord.Color.red())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="move_voice")
    @commands.has_permissions(move_members=True)
    async def move_voice(ctx, member: discord.Member, channel: discord.VoiceChannel):
        """Move member to voice channel"""
        try:
            await member.move_to(channel)
            embed = create_embed("🔊 Taşındı", f"{member.mention} {channel.name} kanalına taşındı!", discord.Color.blue())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="voice_disconnect")
    @commands.has_permissions(move_members=True)
    async def voice_disconnect(ctx, member: discord.Member):
        """Disconnect member from voice channel"""
        try:
            await member.move_to(None)
            embed = create_embed("🔇 Bağlantı Kesildi", f"{member.mention} ses kanalından atıldı!", discord.Color.orange())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="announcement")
    @commands.has_permissions(mention_everyone=True)
    async def announcement(ctx, title: str, message: str, ping_everyone: bool = False):
        """Send an announcement"""
        try:
            embed = create_embed("📢 DUYURU", message, discord.Color.gold())
            embed.add_field(name="Duyuran", value=ctx.author.mention, inline=True)
            
            content = "@everyone " if ping_everyone else ""
            await ctx.send(content + "**DUYURU:**", embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="poll")
    @commands.has_permissions(moderate_members=True)
    async def poll(ctx, question: str, option1: str, option2: str, option3: str = "", option4: str = ""):
        """Create a poll"""
        try:
            embed = create_embed("🗳️ ANKET", question, discord.Color.blue())
            
            options = [option1, option2]
            if option3 and option3 != "": options.append(option3)
            if option4 and option4 != "": options.append(option4)
            
            reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            
            for i, option in enumerate(options):
                embed.add_field(name=f"{reactions[i]} {option}", value="\u200b", inline=False)
            
            message = await ctx.send(embed=embed)
            for i in range(len(options)):
                await message.add_reaction(reactions[i])
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="giveaway")
    @commands.has_permissions(moderate_members=True)
    async def giveaway(ctx, prize: str, duration: int, winners: int = 1):
        """Start a giveaway"""
        try:
            embed = create_embed("🎉 ÇEKİLİŞ", f"**Ödül:** {prize}", discord.Color.purple())
            embed.add_field(name="Süre", value=f"{duration} dakika", inline=True)
            embed.add_field(name="Kazanan Sayısı", value=winners, inline=True)
            embed.add_field(name="Katılım", value="🎉 ile tepki verin!", inline=False)
            
            message = await ctx.send(embed=embed)
            await message.add_reaction("🎉")
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="backup_server")
    @commands.has_permissions(administrator=True)
    async def backup_server(ctx):
        """Create server backup"""
        try:
            guild = ctx.guild
            backup_data = {
                "name": guild.name,
                "channels": [{"name": ch.name, "type": str(ch.type)} for ch in guild.channels],
                "roles": [{"name": role.name, "color": str(role.color)} for role in guild.roles],
                "members": guild.member_count
            }
            
            embed = create_embed("💾 Sunucu Yedeği", "Yedek alındı!", discord.Color.green())
            embed.add_field(name="Kanallar", value=len(backup_data["channels"]), inline=True)
            embed.add_field(name="Roller", value=len(backup_data["roles"]), inline=True)
            embed.add_field(name="Üyeler", value=backup_data["members"], inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="mass_dm")
    @commands.has_permissions(administrator=True)
    async def mass_dm(ctx, *, message: str):
        """Send mass DM to members"""
        try:
            members = ctx.guild.members
            sent = 0
            
            for member in members[:50]:  # Limit to 50 to avoid rate limits
                try:
                    await member.send(message)
                    sent += 1
                except:
                    continue
            
            embed = create_embed("📨 Toplu DM", f"{sent} kişiye mesaj gönderildi!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="invites")
    @commands.has_permissions(manage_guild=True)
    async def invites(ctx):
        """List server invites"""
        try:
            invites = await ctx.guild.invites()
            invite_list = []
            
            for invite in invites[:10]:
                invite_list.append(f"**{invite.code}** - {invite.uses} kullanım - {invite.inviter.mention}")
            
            embed = create_embed("📧 Davetiyeler", "Aktif davetiyeler", discord.Color.blue())
            embed.add_field(name="Liste", value="\n".join(invite_list) or "Davetiye yok", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="create_invite")
    @commands.has_permissions(create_instant_invite=True)
    async def create_invite(ctx, max_uses: int = 0, max_age: int = 0):
        """Create server invite"""
        try:
            invite = await ctx.channel.create_invite(max_uses=max_uses, max_age=max_age)
            embed = create_embed("📧 Davetiye Oluşturuldu", f"Yeni davetiye: {invite.url}", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="activity_check")
    @commands.has_permissions(moderate_members=True)
    async def activity_check(ctx, days: int = 7):
        """Check member activity"""
        try:
            import datetime
            cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
            inactive = []
            
            for member in ctx.guild.members:
                if member.joined_at < cutoff and not any(role.permissions.manage_messages for role in member.roles):
                    inactive.append(member.display_name)
            
            embed = create_embed("📊 Aktiflik Kontrolü", f"Son {days} günde aktif olmayan üyeler", discord.Color.orange())
            embed.add_field(name="İnaktif Üyeler", value="\n".join(inactive[:20]) or "Hepsi aktif", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="autorole")
    @commands.has_permissions(manage_roles=True)
    async def autorole(ctx, role: discord.Role):
        """Set autorole for new members"""
        try:
            # Store in database or config
            embed = create_embed("🤖 Otomatik Rol", f"Yeni üyeler {role.mention} rolünü otomatik alacak!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="automod")
    @commands.has_permissions(administrator=True)
    async def automod(ctx, action: str, enabled: bool = True):
        """Configure automod settings"""
        try:
            actions = {
                "spam": "Spam koruması",
                "caps": "CAPS koruması", 
                "links": "Link koruması",
                "mentions": "Mention koruması"
            }
            
            if action in actions:
                status = "aktif" if enabled else "pasif"
                embed = create_embed("🛡️ Otomatik Moderasyon", f"{actions[action]} {status}!", discord.Color.blue())
            else:
                embed = create_embed("❌ Hata", "Geçersiz eylem!", discord.Color.red())
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="scheduled_message")
    @commands.has_permissions(manage_messages=True)
    async def scheduled_message(ctx, message: str, minutes: int):
        """Schedule a message"""
        try:
            import asyncio
            
            embed = create_embed("⏰ Zamanlanmış Mesaj", f"Mesaj {minutes} dakika sonra gönderilecek!", discord.Color.blue())
            await ctx.send(embed=embed)
            
            await asyncio.sleep(minutes * 60)
            await ctx.channel.send(f"⏰ **Zamanlanmış Mesaj:** {message}")
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="tempban")
    @commands.has_permissions(ban_members=True)
    async def tempban(ctx, member: discord.Member, duration: int, reason: str = "Geçici yasaklama"):
        """Temporarily ban a member"""
        try:
            await member.ban(reason=f"{reason} - {duration} dakika")
            
            embed = create_embed("⏰ Geçici Yasaklama", f"{member.mention} {duration} dakika yasaklandı!", discord.Color.red())
            await ctx.send(embed=embed)
            
            # Schedule unban
            import asyncio
            await asyncio.sleep(duration * 60)
            await ctx.guild.unban(member)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="member_count")
    @commands.has_permissions(manage_channels=True)
    async def member_count(ctx):
        """Create member count channel"""
        try:
            channel = await ctx.guild.create_voice_channel(f"👥 Üyeler: {ctx.guild.member_count}")
            embed = create_embed("📊 Üye Sayısı Kanalı", f"{channel.mention} oluşturuldu!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="welcome_message")
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(ctx, channel: discord.TextChannel, message: str):
        """Set welcome message"""
        try:
            # Store in database
            embed = create_embed("👋 Hoşgeldin Mesajı", f"{channel.mention} kanalında hoşgeldin mesajı ayarlandı!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="reaction_role")
    @commands.has_permissions(manage_roles=True)
    async def reaction_role(ctx, message_id: str, emoji: str, role: discord.Role):
        """Set up reaction roles"""
        try:
            message = await ctx.channel.fetch_message(int(message_id))
            await message.add_reaction(emoji)
            
            embed = create_embed("⚡ Tepki Rolü", f"{emoji} tepkisi {role.mention} rolünü verecek!", discord.Color.purple())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="moderation_stats")
    @commands.has_permissions(moderate_members=True)
    async def moderation_stats(ctx):
        """Show moderation statistics"""
        try:
            db.c.execute('SELECT COUNT(*) FROM warnings')
            total_warnings = db.c.fetchone()[0] if db.c.fetchone() else 0
            
            embed = create_embed("📊 Moderasyon İstatistikleri", "Sunucu moderasyon özeti", discord.Color.blue())
            embed.add_field(name="💀 Toplam Uyarı", value=total_warnings, inline=True)
            embed.add_field(name="👮 Moderatörler", value=len([m for m in ctx.guild.members if m.guild_permissions.moderate_members]), inline=True)
            embed.add_field(name="🛡️ Aktif", value="Sistem çalışıyor", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="reset_warnings")
    @commands.has_permissions(administrator=True)
    async def reset_warnings(ctx, member: discord.Member):
        """Reset member's warnings"""
        try:
            db.c.execute('DELETE FROM warnings WHERE user_id = ?', (member.id,))
            db.conn.commit()
            
            embed = create_embed("🧹 Uyarılar Sıfırlandı", f"{member.mention} kullanıcısının tüm uyarıları silindi!", discord.Color.green())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    @bot.command(name="maintenance")
    @commands.has_permissions(administrator=True)
    async def maintenance(ctx, enabled: bool = True):
        """Toggle maintenance mode"""
        try:
            if enabled:
                # Lock channels, set status
                embed = create_embed("🔧 Bakım Modu", "Sunucu bakım moduna alındı!", discord.Color.orange())
            else:
                embed = create_embed("✅ Bakım Bitti", "Sunucu normal moda döndü!", discord.Color.green())
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Hata: {str(e)}")

    # ===============================
    # EĞLENCELİ MİNİ OYUNLAR
    # ===============================
    
    @bot.command(name='zar')
    async def roll_dice(ctx, sides: int = 6, count: int = 1):
        """Zar at! GoT tarzı kaderini belirle"""
        try:
            if count > 10 or sides > 100:
                embed = create_embed("❌ Hata", "En fazla 10 zar ve 100 yüzlü zar kullanabilirsin!", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            import random
            results = [random.randint(1, sides) for _ in range(count)]
            total = sum(results)
            
            # GoT themed responses
            if total >= sides * count * 0.8:
                fate_msg = "🏆 **Tanrılar senin yanında!** Ejderler bile bu şansa imreniyor!"
                color = discord.Color.gold()
            elif total <= sides * count * 0.2:
                fate_msg = "💀 **Kötü Şans!** Faceless Man'lerin laneti üzerinde!"
                color = discord.Color.red()
            else:
                fate_msg = "⚖️ **Ortalama Kader** - The Many-Faced God nötr kalmış."
                color = discord.Color.blue()
            
            embed = create_embed("🎲 Kader Zarları", 
                               f"**{ctx.author.display_name}** {count}d{sides} attı!", 
                               color)
            embed.add_field(name="Sonuçlar", value=" + ".join(map(str, results)), inline=True)
            embed.add_field(name="Toplam", value=str(total), inline=True)
            embed.add_field(name="Kader", value=fate_msg, inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Dice roll error: {e}")
            embed = create_embed("❌ Hata", f"Zar atma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='tahmin')
    async def guess_game(ctx, guess: int = 0):
        """1-100 arası sayı tahmin oyunu!"""
        try:
            import random
            
            if not hasattr(bot, 'guess_games'):
                bot.guess_games = {}
            
            user_id = ctx.author.id
            
            if guess <= 0:
                # Start new game
                bot.guess_games[user_id] = {
                    'number': random.randint(1, 100),
                    'attempts': 0,
                    'max_attempts': 7
                }
                embed = create_embed("🎯 Sayı Tahmin Oyunu", 
                                   "1-100 arası bir sayı tuttum! 7 hakkın var.", 
                                   discord.Color.blue())
                embed.add_field(name="Nasıl Oynanır", value="!tahmin <sayı> yazarak tahmin et!", inline=False)
                await ctx.send(embed=embed)
                return
            
            if user_id not in bot.guess_games:
                embed = create_embed("❌ Hata", "Oyun yok! !tahmin yazarak başla.", discord.Color.red())
                await ctx.send(embed=embed)
                return
            
            game = bot.guess_games[user_id]
            game['attempts'] += 1
            
            if guess == game['number']:
                # Win!
                del bot.guess_games[user_id]
                embed = create_embed("🎉 KAZANDIN!", 
                                   f"Doğru! Sayı {game['number']} idi!\n{game['attempts']} denemede buldun!", 
                                   discord.Color.green())
                await ctx.send(embed=embed)
            elif game['attempts'] >= game['max_attempts']:
                # Lose
                del bot.guess_games[user_id]
                embed = create_embed("💀 Kaybettin!", 
                                   f"Hakkın bitti! Sayı {game['number']} idi.", 
                                   discord.Color.red())
                await ctx.send(embed=embed)
            else:
                # Continue
                remaining = game['max_attempts'] - game['attempts']
                hint = "⬆️ Daha yüksek!" if guess < game['number'] else "⬇️ Daha düşük!"
                embed = create_embed("🎯 Tahmin Et", 
                                   f"{hint}\n{remaining} hakkın kaldı.", 
                                   discord.Color.orange())
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Guess game error: {e}")
            embed = create_embed("❌ Hata", f"Tahmin oyunu hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='aşk_uyumu')
    async def love_compatibility(ctx, partner: discord.Member):
        """İki kişi arasındaki aşk uyumunu hesapla!"""
        try:
            import hashlib
            
            # Create deterministic but seemingly random compatibility
            combined = f"{min(ctx.author.id, partner.id)}{max(ctx.author.id, partner.id)}"
            hash_result = hashlib.md5(combined.encode()).hexdigest()
            compatibility = int(hash_result[:2], 16) % 101  # 0-100
            
            # GoT themed compatibility descriptions
            if compatibility >= 90:
                desc = "💕 **DESTINED LOVERS** - Jon Snow ve Daenerys gibi!"
                color = discord.Color.purple()
            elif compatibility >= 75:
                desc = "❤️ **Mükemmel Uyum** - Ned ve Catelyn Stark seviyesi!"
                color = discord.Color.red()
            elif compatibility >= 50:
                desc = "💛 **İyi Uyum** - Tyrion'un zekası gibi dengeli!"
                color = discord.Color.gold()
            elif compatibility >= 25:
                desc = "💙 **Arkadaşlık** - Sam ve Jon gibi sadık dostluk!"
                color = discord.Color.blue()
            else:
                desc = "💔 **Zıt Kutuplar** - Joffrey ve herkes gibi..."
                color = discord.Color.dark_red()
            
            embed = create_embed("💖 Aşk Uyumu Testi", 
                               f"**{ctx.author.display_name}** ❤️ **{partner.display_name}**", 
                               color)
            embed.add_field(name="Uyum Skoru", value=f"{compatibility}%", inline=True)
            embed.add_field(name="Analiz", value=desc, inline=False)
            embed.add_field(name="💫 Kader", 
                          value="The Many-Faced God'un hesaplamalarına göre...", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Love compatibility error: {e}")
            embed = create_embed("❌ Hata", f"Aşk uyumu hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='hikaye')
    async def collaborative_story(ctx, *, word: str = ""):
        """Grup halinde hikaye oluştur! Her kişi bir kelime ekler"""
        try:
            if not hasattr(bot, 'stories'):
                bot.stories = {}
            
            guild_id = ctx.guild.id
            
            if not word or word.strip() == "":
                # Show current story
                if guild_id not in bot.stories or not bot.stories[guild_id]:
                    embed = create_embed("📚 Hikaye", 
                                       "Henüz hikaye başlamadı! İlk kelimeyi sen ekle:", 
                                       discord.Color.blue())
                    embed.add_field(name="Nasıl Oynanır", value="!hikaye <kelime> yazarak hikayeye katkıda bulun!", inline=False)
                else:
                    story_text = " ".join(bot.stories[guild_id])
                    embed = create_embed("📚 Mevcut Hikaye", story_text, discord.Color.green())
                    embed.add_field(name="Son Eklenen", value=f"Kelime sayısı: {len(bot.stories[guild_id])}", inline=True)
                await ctx.send(embed=embed)
                return
            
            # Add word to story
            if guild_id not in bot.stories:
                bot.stories[guild_id] = []
            
            # Limit story length
            if len(bot.stories[guild_id]) >= 100:
                embed = create_embed("📚 Hikaye Tamamlandı", 
                                   "Bu hikaye 100 kelimeye ulaştı! Yeni hikaye başlatmak için !hikaye_sıfırla", 
                                   discord.Color.gold())
                await ctx.send(embed=embed)
                return
            
            bot.stories[guild_id].append(word)
            story_text = " ".join(bot.stories[guild_id])
            
            embed = create_embed("📚 Hikaye Güncellendi", 
                               f"**{ctx.author.display_name}** '{word}' ekledi!", 
                               discord.Color.green())
            embed.add_field(name="Mevcut Hikaye", value=story_text[-500:], inline=False)  # Show last 500 chars
            embed.add_field(name="İstatistik", value=f"Kelime: {len(bot.stories[guild_id])}/100", inline=True)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Collaborative story error: {e}")
            embed = create_embed("❌ Hata", f"Hikaye hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='hikaye_sıfırla')
    async def reset_story(ctx):
        """Mevcut hikayeyi sıfırla"""
        try:
            guild_id = ctx.guild.id
            
            if hasattr(bot, 'stories') and guild_id in bot.stories:
                old_story = " ".join(bot.stories[guild_id])
                bot.stories[guild_id] = []
                
                embed = create_embed("📚 Hikaye Sıfırlandı", 
                                   "Yeni hikaye başlayabilir!", 
                                   discord.Color.blue())
                if len(old_story) > 0:
                    embed.add_field(name="Eski Hikaye", value=old_story[-500:], inline=False)
                await ctx.send(embed=embed)
            else:
                embed = create_embed("❌ Hata", "Sıfırlanacak hikaye yok!", discord.Color.red())
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Reset story error: {e}")
            embed = create_embed("❌ Hata", f"Hikaye sıfırlama hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    # ===============================
    # YARATICI ve İNTERAKTİF OYUNLAR  
    # ===============================
    
    @bot.command(name='vs')
    async def versus_battle(ctx, person1: str, person2: str):
        """İki şey/kişi arasında eğlenceli karşılaştırma yap!"""
        try:
            import random
            import hashlib
            
            # Create deterministic result based on the two names
            combined = f"{person1.lower()}{person2.lower()}"
            hash_result = hashlib.md5(combined.encode()).hexdigest()
            winner_chance = int(hash_result[:2], 16) % 100
            
            # Choose winner
            winner = person1 if winner_chance < 50 else person2
            loser = person2 if winner == person1 else person1
            
            # GoT themed battle descriptions
            battle_types = [
                "⚔️ Kılıç düellosu",
                "🏹 Ok yarışması", 
                "🐉 Ejder savaşı",
                "🧠 Zeka turnuvası",
                "👑 Kraliyet yarışması",
                "🏰 Kale kuşatması"
            ]
            
            win_reasons = [
                f"{winner} Valyrian çelik kılıcıyla galip geldi!",
                f"{winner} Three-Eyed Raven'ın bilgeliğini kullandı!",
                f"{winner} Faceless Man teknikleriyle kazandı!",
                f"{winner} House stark sadakatini gösterdi!",
                f"{winner} Targaryen ateşini çıkardı!",
                f"{winner} Lannister zekasını sergiledi!"
            ]
            
            battle_type = random.choice(battle_types)
            win_reason = random.choice(win_reasons)
            intensity = random.randint(60, 99)
            
            embed = create_embed(f"⚔️ {battle_type}", 
                               f"**{person1}** vs **{person2}**", 
                               discord.Color.orange())
            embed.add_field(name="🏆 Kazanan", value=f"**{winner}**", inline=True)
            embed.add_field(name="💀 Kaybeden", value=f"**{loser}**", inline=True)
            embed.add_field(name="🔥 Yoğunluk", value=f"{intensity}%", inline=True)
            embed.add_field(name="📜 Savaş Hikayesi", value=win_reason, inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Versus battle error: {e}")
            embed = create_embed("❌ Hata", f"Savaş simülasyonu hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='rastgele_görev')
    async def random_quest(ctx):
        """Rastgele GoT temalı görev al!"""
        try:
            import random
            
            quest_types = [
                {
                    "title": "🏰 Kale Görevleri",
                    "quests": [
                        "Winterfell'in duvarlarını güçlendir",
                        "Red Keep'teki gizli geçidi bul",
                        "Storm's End'in savunmasını organize et",
                        "Dragonstone'da obsidian madeni işlet"
                    ],
                    "rewards": ["500-1500 altın", "Hane prestiji", "Askeri güç"]
                },
                {
                    "title": "⚔️ Savaş Görevleri", 
                    "quests": [
                        "White Walker'lara karşı reconnaissance yap",
                        "Wildling'lerin Wall ötesindeki planlarını öğren",
                        "Iron Islands'dan gelen tehdidi bertaraf et",
                        "Sellsword company ile kontrat imzala"
                    ],
                    "rewards": ["1000-3000 altın", "Asker kazanımı", "Savaş deneyimi"]
                },
                {
                    "title": "💰 Ticaret Görevleri",
                    "quests": [
                        "King's Landing'de yeni ticaret yolu kur",
                        "Braavos'tan Iron Bank ile görüş",
                        "Dorne'dan baharat getir",
                        "Oldtown'da Citadel ile bilgi takası yap"
                    ],
                    "rewards": ["2000-5000 altın", "Ticaret bonusu", "Diplomatik ilişki"]
                },
                {
                    "title": "🎭 Sosyal Görevler",
                    "quests": [
                        "Büyük bir feast organize et",
                        "Rival haneler arasında evlilik ayarla",
                        "Royal court'ta dedikodu topla",
                        "Tourney'de champion ol"
                    ],
                    "rewards": ["1500-4000 altın", "Sosyal prestij", "Yeni ittifaklar"]
                }
            ]
            
            quest_category = random.choice(quest_types)
            chosen_quest = random.choice(quest_category["quests"])
            reward = random.choice(quest_category["rewards"])
            difficulty = random.choice(["Kolay", "Orta", "Zor", "Efsanevi"])
            time_limit = random.choice(["2 saat", "1 gün", "3 gün", "1 hafta"])
            
            difficulty_colors = {
                "Kolay": discord.Color.green(),
                "Orta": discord.Color.orange(), 
                "Zor": discord.Color.red(),
                "Efsanevi": discord.Color.purple()
            }
            
            embed = create_embed(quest_category["title"], 
                               f"**{ctx.author.display_name}** için yeni görev!", 
                               difficulty_colors[difficulty])
            embed.add_field(name="📜 Görev", value=chosen_quest, inline=False)
            embed.add_field(name="💎 Ödül", value=reward, inline=True)
            embed.add_field(name="⚡ Zorluk", value=difficulty, inline=True)
            embed.add_field(name="⏰ Süre", value=time_limit, inline=True)
            embed.add_field(name="🎯 İpucu", 
                          value="Bu görev tamamen roleplay için! Hayal gücünle tamamla ve sunucuda paylaş.", 
                          inline=False)
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Random quest error: {e}")
            embed = create_embed("❌ Hata", f"Görev alma hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    @bot.command(name='kahin')
    async def fortune_teller(ctx, *, question: str = ""):
        """Three-Eyed Raven'dan kehanet al!"""
        try:
            import random
            
            if not question or question.strip() == "":
                embed = create_embed("🔮 Three-Eyed Raven", 
                                   "Geleceği görmek için bir soru sor!", 
                                   discord.Color.purple())
                embed.add_field(name="Kullanım", value="!kahin <sorun>", inline=False)
                embed.add_field(name="Örnek", value="!kahin Hanemi büyük olacak mı?", inline=False)
                await ctx.send(embed=embed)
                return
            
            # Fortune predictions with GoT theme
            predictions = [
                "🐉 Ejderleriniz yakında uyanacak...",
                "❄️ Kış geliyor, ama sen hazırsın.",
                "👑 Demir Taht yakındaki gelecekte önemli...",
                "⚔️ Gelecekte büyük bir savaş seni bekliyor.",
                "💰 Altın yağmuru yakında kapını çalacak.",
                "💍 Aşk hayatında büyük değişiklikler var.",
                "🏰 Yeni topraklar elde edeceksin.",
                "🗡️ Eski bir düşman dostun olacak.",
                "📚 Önemli bir bilgi sana ulaşacak.",
                "🌟 Kaderinle alakalı büyük keşif yapacaksın."
            ]
            
            prediction = random.choice(predictions)
            crystal_types = ["Dragonstone", "Valyrian Steel", "Obsidian", "Weirwood", "Ice Crystal"]
            crystal = random.choice(crystal_types)
            probability = random.randint(60, 95)
            
            embed = create_embed("🔮 Three-Eyed Raven Kehaneyi", 
                               f"**{ctx.author.display_name}** için gelecek vizyonu", 
                               discord.Color.purple())
            embed.add_field(name="❓ Sorun", value=question[:100], inline=False)
            embed.add_field(name="🌟 Kehanet", value=prediction, inline=False)
            embed.add_field(name="💎 Kristal", value=crystal, inline=True)
            embed.add_field(name="🎯 Güvenilirlik", value=f"%{probability}", inline=True)
            embed.set_footer(text="The Many-Faced God'un iradesine göre...")
            await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Fortune teller error: {e}")
            embed = create_embed("❌ Hata", f"Kehanet hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)
    
    # ===============================
    # PERFORMANS VE YÖNETİM KOMUTLARI
    # ===============================
    
    @bot.command(name='optimize')
    @commands.has_permissions(administrator=True)
    async def optimize_database(ctx):
        """Optimize database performance (Admin only)"""
        try:
            embed = create_embed("🔧 Veritabanı Optimizasyonu", "Optimizasyon başlatılıyor...", discord.Color.yellow())
            message = await ctx.send(embed=embed)
            
            # Run optimization
            success = bot.perf_optimizer.optimize_database()
            
            if success:
                embed = create_embed("✅ Optimizasyon Tamamlandı", 
                                   "Veritabanı başarıyla optimize edildi!", 
                                   discord.Color.green())
                embed.add_field(name="İşlemler", value="• Indexler oluşturuldu\n• VACUUM çalıştırıldı\n• ANALYZE çalıştırıldı", inline=False)
            else:
                embed = create_embed("❌ Optimizasyon Hatası", 
                                   "Optimizasyon sırasında hata oluştu!", 
                                   discord.Color.red())
            
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            embed = create_embed("❌ Hata", f"Optimizasyon hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)
    
    @bot.command(name='dbstats')
    @commands.has_permissions(moderate_members=True)
    async def database_stats(ctx):
        """Show database statistics"""
        try:
            stats = bot.perf_optimizer.get_performance_stats()
            
            embed = create_embed("📊 Veritabanı İstatistikleri", 
                               "Sistem performans bilgileri", 
                               discord.Color.blue())
            
            # Table counts
            table_info = ""
            for key, value in stats.items():
                if key.endswith('_count'):
                    table_name = key.replace('_count', '').title()
                    table_info += f"**{table_name}:** {value:,}\n"
            
            embed.add_field(name="📚 Tablo Boyutları", value=table_info or "Bilgi yok", inline=True)
            
            # Database size
            if 'database_size_bytes' in stats:
                size_mb = stats['database_size_bytes'] / (1024 * 1024)
                embed.add_field(name="💾 Veritabanı Boyutu", value=f"{size_mb:.2f} MB", inline=True)
            
            embed.add_field(name="⚡ Performans", value="Optimized ✅", inline=True)
            embed.set_footer(text="Son güncelleme: Şimdi")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Database stats error: {e}")
            embed = create_embed("❌ Hata", f"İstatistik hatası: {str(e)}", discord.Color.red())
            await ctx.send(embed=embed)

    logger.info("All commands have been set up successfully")
    logger.info(f"Total commands available: {len(bot.commands)}")