import discord
from discord.ext import commands
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number, get_house_emoji

logger = logging.getLogger(__name__)

class LoreEconomicSystem:
    def __init__(self, database):
        self.db = database
        
        # Game of Thrones kitaplarına göre gerçek hane zenginlikleri
        self.lore_house_wealth = {
            # MEGA ZENGIN HANELER
            "Lannister": {
                "gold": 2500000,  # Casterly Rock altın madenleri
                "income_sources": [
                    {"name": "Casterly Rock Altın Madenleri", "type": "mining", "income": 5000, "description": "En zengin altın madenleri"},
                    {"name": "Lannisport Ticaret", "type": "trade", "income": 3000, "description": "Büyük liman kenti"},
                    {"name": "Westerlands Vergileri", "type": "tax", "income": 2000, "description": "Bölge vergi toplama"}
                ],
                "population": 150000,
                "soldiers": 60000
            },
            "Tyrell": {
                "gold": 1800000,  # Reach'in zenginliği
                "income_sources": [
                    {"name": "Highgarden Tarım", "type": "agriculture", "income": 4000, "description": "En verimli topraklar"},
                    {"name": "Oldtown Ticaret", "type": "trade", "income": 2500, "description": "Citadel ve büyük liman"},
                    {"name": "Reach Şarap Üretimi", "type": "luxury", "income": 1500, "description": "En iyi şaraplar"}
                ],
                "population": 200000,
                "soldiers": 100000
            },
            
            # ÇÜNKÜ HANELER  
            "Stark": {
                "gold": 800000,  # Kuzey hanesi, zengin değil ama güçlü
                "income_sources": [
                    {"name": "Winterfell Vergileri", "type": "tax", "income": 1500, "description": "Kuzey lordlarından vergi"},
                    {"name": "White Harbor Ticaret", "type": "trade", "income": 1200, "description": "Kuzey'in tek büyük limanı"},
                    {"name": "Orman Ürünleri", "type": "resources", "income": 800, "description": "Kereste ve av"}
                ],
                "population": 120000,
                "soldiers": 45000
            },
            "Baratheon": {
                "gold": 600000,  # Robert'ın harcamaları yüzünden azalmış
                "income_sources": [
                    {"name": "Storm's End Vergileri", "type": "tax", "income": 1000, "description": "Stormlands vergileri"},
                    {"name": "Shipbreaker Bay Balıkçılık", "type": "fishing", "income": 600, "description": "Deniz ürünleri"},
                    {"name": "Kingswood Avcılık", "type": "hunting", "income": 400, "description": "Av ve kereste"}
                ],
                "population": 80000,
                "soldiers": 30000
            },
            
            # ORTA GELİRLİ HANELER
            "Arryn": {
                "gold": 700000,  # Vale'in zenginliği
                "income_sources": [
                    {"name": "Eyrie Vergileri", "type": "tax", "income": 1200, "description": "Vale lordlarından vergi"},
                    {"name": "Gulltown Ticaret", "type": "trade", "income": 800, "description": "Vale'in liman kenti"},
                    {"name": "Dağ Madenleri", "type": "mining", "income": 500, "description": "Demir ve gümüş"}
                ],
                "population": 90000,
                "soldiers": 35000
            },
            "Tully": {
                "gold": 500000,  # Riverlands orta düzey
                "income_sources": [
                    {"name": "Riverrun Vergileri", "type": "tax", "income": 800, "description": "Riverlands vergileri"},
                    {"name": "Nehir Ticareti", "type": "trade", "income": 600, "description": "Trident nehri ticareti"},
                    {"name": "Balıkçılık", "type": "fishing", "income": 400, "description": "Tatlı su balıkları"}
                ],
                "population": 70000,
                "soldiers": 25000
            },
            "Martell": {
                "gold": 900000,  # Dorne'un zenginliği
                "income_sources": [
                    {"name": "Sunspear Ticaret", "type": "trade", "income": 1500, "description": "Essos ile ticaret"},
                    {"name": "Dornish Şarap & Baharat", "type": "luxury", "income": 1000, "description": "Lüks ürünler"},
                    {"name": "Çöl Oazları", "type": "agriculture", "income": 500, "description": "Nadir mahsuller"}
                ],
                "population": 100000,
                "soldiers": 40000
            },
            
            # FAKIR/ZAYIF HANELER
            "Greyjoy": {
                "gold": 300000,  # Iron Islands fakir
                "income_sources": [
                    {"name": "Pyke Vergileri", "type": "tax", "income": 400, "description": "Iron Islands vergileri"},
                    {"name": "Balıkçılık & Denizcilik", "type": "fishing", "income": 600, "description": "Deniz ürünleri"},
                    {"name": "Yağmalama", "type": "raiding", "income": 800, "description": "Korsanlık geliri"}
                ],
                "population": 50000,
                "soldiers": 20000
            },
            "Bolton": {
                "gold": 200000,  # Küçük kuzey hanesi
                "income_sources": [
                    {"name": "Dreadfort Vergileri", "type": "tax", "income": 300, "description": "Küçük lordluk"},
                    {"name": "Deri İşçiliği", "type": "crafting", "income": 200, "description": "Özel deri işleri"},
                    {"name": "Korku Vergisi", "type": "extortion", "income": 400, "description": "Zorla toplanan vergi"}
                ],
                "population": 30000,
                "soldiers": 15000
            },
            "Mormont": {
                "gold": 100000,  # Bear Island çok fakir
                "income_sources": [
                    {"name": "Bear Island Balıkçılık", "type": "fishing", "income": 200, "description": "Küçük ada balıkçılığı"},
                    {"name": "Ayı Derisi Ticareti", "type": "hunting", "income": 150, "description": "Ayı avı"},
                    {"name": "Night's Watch Bağışı", "type": "donation", "income": 100, "description": "Gece Nöbeti desteği"}
                ],
                "population": 10000,
                "soldiers": 5000
            }
        }
        
        # Kaynak türleri ve özellikleri
        self.resource_types = {
            "gold": {"name": "Altın", "emoji": "💰", "base_value": 1},
            "food": {"name": "Yiyecek", "emoji": "🌾", "base_value": 2},
            "stone": {"name": "Taş", "emoji": "🗿", "base_value": 5},
            "wood": {"name": "Kereste", "emoji": "🪵", "base_value": 3},
            "iron": {"name": "Demir", "emoji": "⚔️", "base_value": 8},
            "cloth": {"name": "Kumaş", "emoji": "🧵", "base_value": 4},
            "wine": {"name": "Şarap", "emoji": "🍷", "base_value": 12},
            "spices": {"name": "Baharat", "emoji": "🌶️", "base_value": 15}
        }
        
        self.setup_lore_tables()
    
    def setup_lore_tables(self):
        """Create lore-based economic tables"""
        try:
            # Kaynak üretim tesisleri
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS resource_facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                house_id INTEGER NOT NULL,
                facility_name TEXT NOT NULL,
                facility_type TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                production_rate INTEGER NOT NULL,
                maintenance_cost INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (house_id) REFERENCES alliances (id)
            )
            ''')
            
            # Kaynak depoları
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS resource_storage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                house_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(house_id, resource_type),
                FOREIGN KEY (house_id) REFERENCES alliances (id)
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Lore economic tables created successfully")
        except Exception as e:
            logger.error(f"Error creating lore economic tables: {e}")
    
    def setup_lore_commands(self, bot):
        """Setup lore-based economic commands"""
        
        @bot.command(name='gerçek_ekonomi_kur')
        async def setup_lore_economy(ctx):
            """Kitaplardaki gerçek verilere göre ekonomiyi kur"""
            try:
                embed = create_embed(
                    "⚙️ GERÇEKÇİ EKONOMİ KURULUYOR",
                    "Game of Thrones kitaplarındaki gerçek veriler uygulanıyor...",
                    discord.Color.gold()
                )
                
                setup_msg = await ctx.send(embed=embed)
                
                updated_houses = 0
                created_facilities = 0
                
                # Tüm haneleri güncelle
                for house_name, house_data in self.lore_house_wealth.items():
                    # Haneyi bul
                    self.db.c.execute('SELECT id FROM alliances WHERE name = ?', (house_name,))
                    result = self.db.c.fetchone()
                    
                    if result:
                        house_id = result[0]
                        
                        # Altın miktarını güncelle
                        self.db.c.execute('''
                        UPDATE alliances SET gold = ?, soldiers = ?
                        WHERE id = ?
                        ''', (house_data['gold'], house_data['soldiers'], house_id))
                        
                        # Gelir kaynaklarını ekle
                        for source in house_data['income_sources']:
                            self.db.c.execute('''
                            INSERT OR REPLACE INTO resource_facilities 
                            (house_id, facility_name, facility_type, resource_type, production_rate)
                            VALUES (?, ?, ?, 'gold', ?)
                            ''', (house_id, source['name'], source['type'], source['income']))
                            created_facilities += 1
                        
                        # Temel kaynak depoları oluştur
                        for resource_type in self.resource_types.keys():
                            base_amount = house_data['gold'] // 1000  # Altına göre temel kaynak
                            self.db.c.execute('''
                            INSERT OR REPLACE INTO resource_storage (house_id, resource_type, quantity)
                            VALUES (?, ?, ?)
                            ''', (house_id, resource_type, base_amount))
                        
                        updated_houses += 1
                
                self.db.conn.commit()
                
                # Sonuç göster
                embed = create_embed(
                    "✅ GERÇEKÇİ EKONOMİ KURULDU!",
                    "Game of Thrones kitaplarındaki gerçek veriler başarıyla uygulandı",
                    discord.Color.green()
                )
                
                embed.add_field(name="🏠 Güncellenen Haneler", value=updated_houses, inline=True)
                embed.add_field(name="🏭 Oluşturulan Tesisler", value=created_facilities, inline=True)
                embed.add_field(name="📊 Kaynak Türleri", value=len(self.resource_types), inline=True)
                
                # En zengin haneleri göster
                wealth_info = ""
                sorted_houses = sorted(self.lore_house_wealth.items(), key=lambda x: x[1]['gold'], reverse=True)[:5]
                for house_name, data in sorted_houses:
                    wealth_info += f"{get_house_emoji(house_name)} **{house_name}**: {format_number(data['gold'])} altın\n"
                
                embed.add_field(name="💰 En Zengin Haneler", value=wealth_info, inline=False)
                
                await setup_msg.edit(embed=embed)
                
            except Exception as e:
                logger.error(f"Setup lore economy error: {e}")
                embed = create_embed("❌ Hata", f"Ekonomi kurulum hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='hane_ekonomi')
        async def house_economy(ctx):
            """Hanenizdeki ekonomik durumu ve tesisleri görüntüle"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Ekonomi durumu görmek için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                alliance_id = alliance[0]
                alliance_data = self.db.get_alliance_by_id(alliance_id)
                house_name = alliance_data[1]
                
                embed = create_embed(
                    f"{get_house_emoji(house_name)} {house_name.upper()} EKONOMİSİ",
                    "Detaylı ekonomik durum ve üretim tesisleri",
                    discord.Color.gold()
                )
                
                # Temel bilgiler
                embed.add_field(name="💰 Hazine", value=f"{format_number(alliance_data[3])} altın", inline=True)
                embed.add_field(name="⚔️ Ordu", value=f"{format_number(alliance_data[4])} asker", inline=True)
                embed.add_field(name="⚡ Güç", value=f"{format_number(alliance_data[5])} puan", inline=True)
                
                # Üretim tesisleri
                self.db.c.execute('''
                SELECT facility_name, facility_type, resource_type, production_rate, level
                FROM resource_facilities WHERE house_id = ?
                ORDER BY production_rate DESC
                ''', (alliance_id,))
                
                facilities = self.db.c.fetchall()
                
                if facilities:
                    facilities_text = ""
                    total_income = 0
                    for facility_name, facility_type, resource_type, production_rate, level in facilities:
                        emoji = "🏭" if facility_type == "mining" else "🌾" if facility_type == "agriculture" else "🚢" if facility_type == "trade" else "🏛️"
                        facilities_text += f"{emoji} **{facility_name}** (Lv.{level})\n"
                        facilities_text += f"   └ {format_number(production_rate)} altın/saat\n\n"
                        total_income += production_rate
                    
                    embed.add_field(name="🏭 Üretim Tesisleri", value=facilities_text[:1000], inline=False)
                    embed.add_field(name="📈 Toplam Gelir", value=f"{format_number(total_income)} altın/saat", inline=True)
                
                # Kaynak depoları
                self.db.c.execute('''
                SELECT resource_type, quantity FROM resource_storage 
                WHERE house_id = ? AND quantity > 0
                ORDER BY quantity DESC
                ''', (alliance_id,))
                
                resources = self.db.c.fetchall()
                
                if resources:
                    resources_text = ""
                    for resource_type, quantity in resources[:6]:  # İlk 6 kaynak
                        if resource_type in self.resource_types:
                            emoji = self.resource_types[resource_type]["emoji"]
                            name = self.resource_types[resource_type]["name"]
                            resources_text += f"{emoji} **{name}**: {format_number(quantity)}\n"
                    
                    embed.add_field(name="📦 Kaynak Depoları", value=resources_text, inline=True)
                
                # Kitaptaki bilgiler varsa ekle
                if house_name in self.lore_house_wealth:
                    lore_data = self.lore_house_wealth[house_name]
                    embed.add_field(name="📚 Kitaptaki Veriler", 
                                  value=f"👥 Nüfus: {format_number(lore_data['population'])}\n"
                                        f"⚔️ Max Ordu: {format_number(lore_data['soldiers'])}\n"
                                        f"💰 Orijinal Servet: {format_number(lore_data['gold'])}", 
                                  inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"House economy error: {e}")
                embed = create_embed("❌ Hata", f"Ekonomi görüntüleme hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='tesis_yükselt')
        async def upgrade_facility(ctx, *, facility_name: str):
            """Üretim tesisini yükselt"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Tesis yükseltmek için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                alliance_id = alliance[0]
                alliance_data = self.db.get_alliance_by_id(alliance_id)
                
                # Tesisi bul
                self.db.c.execute('''
                SELECT id, facility_name, level, production_rate FROM resource_facilities
                WHERE house_id = ? AND facility_name LIKE ?
                ''', (alliance_id, f"%{facility_name}%"))
                
                facility = self.db.c.fetchone()
                
                if not facility:
                    embed = create_embed("❌ Hata", f"'{facility_name}' adında tesis bulunamadı!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                facility_id, full_name, current_level, current_production = facility
                
                # Yükseltme maliyeti hesapla
                upgrade_cost = current_level * 10000  # Her seviye 10k daha pahalı
                new_level = current_level + 1
                new_production = int(current_production * 1.5)  # %50 artış
                
                if alliance_data[3] < upgrade_cost:  # gold check
                    embed = create_embed("❌ Yetersiz Altın", 
                                       f"Yükseltme için {format_number(upgrade_cost)} altın gerekli!", 
                                       discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Yükseltmeyi yap
                self.db.update_alliance_resources(alliance_id, -upgrade_cost, 0)
                
                self.db.c.execute('''
                UPDATE resource_facilities 
                SET level = ?, production_rate = ?
                WHERE id = ?
                ''', (new_level, new_production, facility_id))
                
                self.db.conn.commit()
                
                embed = create_embed(
                    "⬆️ TESİS YÜKSELTİLDİ!",
                    f"**{full_name}** başarıyla yükseltildi!",
                    discord.Color.green()
                )
                
                embed.add_field(name="📊 Eski Seviye", value=f"Lv.{current_level}", inline=True)
                embed.add_field(name="📈 Yeni Seviye", value=f"Lv.{new_level}", inline=True)
                embed.add_field(name="💰 Maliyet", value=f"{format_number(upgrade_cost)} altın", inline=True)
                
                embed.add_field(name="⚡ Eski Üretim", value=f"{format_number(current_production)} altın/saat", inline=True)
                embed.add_field(name="🚀 Yeni Üretim", value=f"{format_number(new_production)} altın/saat", inline=True)
                embed.add_field(name="📈 Artış", value=f"+{format_number(new_production - current_production)} altın/saat", inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Upgrade facility error: {e}")
                embed = create_embed("❌ Hata", f"Tesis yükseltme hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='zenginlik_sıralaması')
        async def wealth_ranking(ctx):
            """Kitaplara göre hanelerin zenginlik sıralaması"""
            try:
                embed = create_embed(
                    "👑 WESTEROS ZENGİNLİK SIRALAMASI",
                    "Game of Thrones kitaplarındaki gerçek verilere göre",
                    discord.Color.gold()
                )
                
                # Kitap verilerine göre sıralama
                sorted_houses = sorted(self.lore_house_wealth.items(), key=lambda x: x[1]['gold'], reverse=True)
                
                ranking_text = ""
                for i, (house_name, data) in enumerate(sorted_houses, 1):
                    if i == 1:
                        ranking_text += f"👑 **{house_name}**: {format_number(data['gold'])} altın\n"
                        ranking_text += f"    └ {len(data['income_sources'])} gelir kaynağı\n\n"
                    elif i == 2:
                        ranking_text += f"🥈 **{house_name}**: {format_number(data['gold'])} altın\n"
                        ranking_text += f"    └ {len(data['income_sources'])} gelir kaynağı\n\n"
                    elif i == 3:
                        ranking_text += f"🥉 **{house_name}**: {format_number(data['gold'])} altın\n"
                        ranking_text += f"    └ {len(data['income_sources'])} gelir kaynağı\n\n"
                    else:
                        ranking_text += f"{i}. **{house_name}**: {format_number(data['gold'])} altın\n"
                
                embed.add_field(name="💰 Zenginlik Sıralaması", value=ranking_text, inline=False)
                
                # En zengin ve en fakir arasındaki fark
                richest = sorted_houses[0][1]['gold']
                poorest = sorted_houses[-1][1]['gold']
                difference = richest / poorest
                
                embed.add_field(name="📊 İstatistikler", 
                              value=f"💎 En Zengin: {format_number(richest)} altın\n"
                                    f"💸 En Fakir: {format_number(poorest)} altın\n"
                                    f"⚖️ Fark Oranı: {difference:.1f}x", 
                              inline=True)
                
                embed.add_field(name="📚 Kaynak", 
                              value="A Song of Ice and Fire kitap serisi\nGeorge R.R. Martin", 
                              inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Wealth ranking error: {e}")
                embed = create_embed("❌ Hata", f"Sıralama hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

logger.info("Lore economic system initialized successfully")