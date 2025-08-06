import discord
from discord.ext import commands
import asyncio
import logging
from utils import create_embed, get_house_emoji
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UserFriendlySystem:
    def __init__(self, db):
        self.db = db
        self.setup_database()

    def setup_database(self):
        """Setup user progress tracking tables"""
        try:
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER PRIMARY KEY,
                tutorial_step INTEGER DEFAULT 0,
                first_join_date TEXT,
                last_help_time TEXT,
                commands_used INTEGER DEFAULT 0,
                difficulty_level TEXT DEFAULT 'beginner'
            )
            ''')

            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS quick_actions (
                user_id INTEGER,
                action_name TEXT,
                last_used TEXT,
                usage_count INTEGER DEFAULT 0
            )
            ''')

            self.db.conn.commit()
            logger.info("User friendly system tables created successfully")
        except Exception as e:
            logger.error(f"Error creating user friendly tables: {e}")

    def setup_user_friendly_commands(self, bot):
        """Setup all user friendly commands"""

        @bot.command(name='başla', aliases=['start', 'begin'])
        async def easy_start(ctx):
            """Super simple start command for new users"""
            user_id = ctx.author.id

            # Track user progress
            self.db.c.execute('''
            INSERT OR REPLACE INTO user_progress (user_id, first_join_date, tutorial_step)
            VALUES (?, ?, 1)
            ''', (user_id, datetime.now().isoformat()))
            self.db.conn.commit()

            embed = create_embed(
                "🏰 WESTEROS'A HOŞGELDİN!",
                f"**{ctx.author.display_name}**, Game of Thrones dünyasına adım attın!\n\n"
                "✨ **Bu bot çok kolay kullanılıyor, endişelenme!**",
                discord.Color.gold()
            )

            embed.add_field(
                name="🎯 İLK 3 KOLAY ADIM",
                value="1️⃣ `!hızlı_hane` - Bir hane seç (2 saniye)\n"
                      "2️⃣ `!hızlı_karakter` - Karakter seç (2 saniye)\n"
                      "3️⃣ `!durum` - Durumunu gör (başardin!)",
                inline=False
            )

            embed.add_field(
                name="🆘 YARDIM LAZIM?",
                value="`!basit_yardım` - Sadece önemli komutlar\n"
                      "`!ne_yapmaliyim` - Sonraki adımı öğren",
                inline=False
            )

            embed.add_field(
                name="💡 İPUCU",
                value="**Kompleks komutları kullanmak zorunda değilsin!**\n"
                      "Basit komutlarla bile çok eğlenebilirsin. 😊",
                inline=False
            )

            await ctx.send(embed=embed)

        @bot.command(name='hızlı_hane', aliases=['quick_house', 'ez_house'])
        async def quick_house_join(ctx):
            """Quick house selection with recommendations"""
            user_id = ctx.author.id

            embed = create_embed(
                "🏰 HIZLI HANE SEÇİMİ",
                "Yeni başlayanlar için **EN İYİ 4 HANE**:",
                discord.Color.blue()
            )

            embed.add_field(
                name="🐺 **STARK** (YENİ BAŞLAYANLAR İÇİN MÜKEMMEL)",
                value="• Güvenilir ve sadık\n• Çok altın kazanırsın\n• Kolay oynanır\n`!katıl Stark`",
                inline=False
            )

            embed.add_field(
                name="🦁 **LANNISTER** (ZENGİN OLMAK İSTİYORSAN)",
                value="• Çok para var\n• Güçlü ekonomi\n• Kolay para kazan\n`!katıl Lannister`",
                inline=False
            )

            embed.add_field(
                name="🐉 **TARGARYEN** (GÜÇLÜ OLMAK İSTİYORSAN)",
                value="• Ejderler!\n• Güçlü savaşçı\n• Havalı görünür\n`!katıl Targaryen`",
                inline=False
            )

            embed.add_field(
                name="🌹 **TYRELL** (SOSYAL VE AKILLI)",
                value="• Çok arkadaş edinirsin\n• Zeka odaklı\n• Sosyal avantajlar\n`!katıl Tyrell`",
                inline=False
            )

            embed.set_footer(text="✨ Yukarıdaki komutlardan birini kopyala-yapıştır! O kadar kolay!")

            await ctx.send(embed=embed)

        @bot.command(name='hızlı_karakter', aliases=['quick_char', 'ez_char'])
        async def quick_character(ctx):
            """Quick character selection with popular choices"""
            user_id = ctx.author.id
            alliance = self.db.get_user_alliance(user_id)

            if not alliance:
                embed = create_embed("❌ Önce Hane Seç",
                                   "Karakter seçmek için önce bir haneye katıl!\n`!hızlı_hane` komutunu kullan.",
                                   discord.Color.red())
                await ctx.send(embed=embed)
                return

            # Get available characters for the house
            house_name = alliance[1]

            from commands import ASOIAF_CHARACTERS

            # Get taken characters
            self.db.c.execute('SELECT character_name FROM asoiaf_characters')
            taken = {row[0] for row in self.db.c.fetchall()}

            # Find available characters for this house
            available = []
            for name, data in ASOIAF_CHARACTERS.items():
                if data["house"] == house_name and name not in taken:
                    available.append((name, data))

            embed = create_embed(
                f"👤 HIZLI KARAKTER SEÇİMİ - {get_house_emoji(house_name)} {house_name}",
                "**Popüler ve kolay karakterler:**",
                discord.Color.purple()
            )

            if available:
                # Show top 3 available characters
                for i, (name, data) in enumerate(available[:3], 1):
                    embed.add_field(
                        name=f"{i}️⃣ **{name}**",
                        value=f"**Unvan:** {data['title']}\n"
                              f"**Yaş:** {data['age']}\n"
                              f"**Komut:** `!karakter {name}`",
                        inline=False
                    )

                embed.add_field(
                    name="💡 NASIL SEÇERİM?",
                    value="Yukarıdaki komutlardan birini **kopyala-yapıştır**!\n"
                          "Örnek: `!karakter Jon Snow`",
                    inline=False
                )
            else:
                embed.add_field(
                    name="😅 Bu Hanede Karakter Kalmamış",
                    value="Başka bir haneye geçebilir veya admin'den yardım isteyebilirsin!",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name='basit_yardım', aliases=['easy_help', 'simple_help'])
        async def simple_help(ctx):
            """Simplified help with only essential commands"""
            user_id = ctx.author.id

            # Update help usage
            self.db.c.execute('''
            UPDATE user_progress SET last_help_time = ? WHERE user_id = ?
            ''', (datetime.now().isoformat(), user_id))
            self.db.conn.commit()

            embed = create_embed(
                "🆘 BASİT YARDIM - SADECE ÖNEMLİ KOMUTLAR",
                "**Karışık komutları unutun! Bunlar yeterli:**",
                discord.Color.green()
            )

            embed.add_field(
                name="🎯 BAŞLANGIÇ (İLK KEZ İSE)",
                value="`!başla` - Başlangıç rehberi\n"
                      "`!hızlı_hane` - Hane seç\n"
                      "`!hızlı_karakter` - Karakter seç",
                inline=False
            )

            embed.add_field(
                name="📊 DURUM KONTROLÜ",
                value="`!durum` - Basit durum\n"
                      "`!altınım` - Param ne kadar?\n"
                      "`!askerlerim` - Asker sayım",
                inline=False
            )

            embed.add_field(
                name="💰 KOLAY PARA KAZANMA",
                value="`!kolay_para` - Hızlı para kazan\n"
                      "`!asker_al` - Asker satın al\n"
                      "`!ticaret_kolay` - Basit ticaret",
                inline=False
            )

            embed.add_field(
                name="⚔️ BASIT SAVAŞ",
                value="`!kolay_savaş` - Savaş teklif et\n"
                      "`!savaşlarım` - Aktif savaşlar\n"
                      "`!barış` - Barış yap",
                inline=False
            )

            embed.add_field(
                name="🎮 EĞLENCE (ZORUNLU DEĞİL)",
                value="`!zar` - Şans zarı at\n"
                      "`!vs` - Karşılaştırma yap\n"
                      "`!roleplay` - RP yap",
                inline=False
            )

            embed.add_field(
                name="🤔 NE YAPACAĞINI BİLMİYORSAN",
                value="`!ne_yapmaliyim` - Sonraki adım\n"
                      "`!ipucu` - Günlük ipucu al",
                inline=False
            )

            embed.set_footer(text="✨ Bu kadar! Daha karışık komutları kullanmak zorunda değilsin.")

            await ctx.send(embed=embed)

        @bot.command(name='ne_yapmaliyim', aliases=['what_next', 'ne_yapayim'])
        async def what_should_i_do(ctx):
            """Smart suggestions based on user progress"""
            user_id = ctx.author.id

            # Get user status
            alliance = self.db.get_user_alliance(user_id)

            self.db.c.execute('SELECT * FROM user_progress WHERE user_id = ?', (user_id,))
            progress = self.db.c.fetchone()

            self.db.c.execute('SELECT * FROM asoiaf_characters WHERE user_id = ?', (user_id,))
            character = self.db.c.fetchone()

            embed = create_embed(
                "🤔 NE YAPMALIYIM?",
                "Durumuna göre **sonraki adımın:**",
                discord.Color.orange()
            )

            if not alliance:
                embed.add_field(
                    name="1️⃣ İLK ÖNCE BU",
                    value="Bir haneye katıl! 👉 `!hızlı_hane`\n"
                          "**Bu olmadan hiçbir şey yapamazsın!**",
                    inline=False
                )
            elif not character:
                embed.add_field(
                    name="2️⃣ SONRA BU",
                    value="Karakter seç! 👉 `!hızlı_karakter`\n"
                          "**Roleplaying için gerekli!**",
                    inline=False
                )
            else:
                # User has both house and character
                gold = alliance[3] if alliance else 0
                soldiers = alliance[4] if alliance else 0

                if gold < 500:
                    embed.add_field(
                        name="💰 PARA KAZAN",
                        value="Az altının var! 👉 `!kolay_para`\n"
                              "**Para olmadan zor!**",
                        inline=False
                    )
                elif soldiers < 200:
                    embed.add_field(
                        name="⚔️ ASKER AL",
                        value="Az askerin var! 👉 `!asker_al 100`\n"
                              "**Güvenlik için gerekli!**",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🎉 HERŞEYİN HAZIR!",
                        value="Artık istediğini yapabilirsin:\n"
                              "• `!kolay_savaş` - Savaş başlat\n"
                              "• `!ticaret_kolay` - Ticaret yap\n"
                              "• `!turnuva_katıl` - Turnuvaya katıl\n"
                              "• `!roleplay` - RP yap",
                        inline=False
                    )

            embed.add_field(
                name="❓ HALA KARIŞIK MI?",
                value="`!basit_yardım` - Sadece temel komutlar\n"
                      "`!ipucu` - Günlük ipucu al",
                inline=False
            )

            await ctx.send(embed=embed)

        @bot.command(name='durum', aliases=['status', 'state'])
        async def simple_status(ctx):
            """Super simple status display"""
            user_id = ctx.author.id
            alliance = self.db.get_user_alliance(user_id)

            if not alliance:
                embed = create_embed(
                    "📊 DURUMUN",
                    "Henüz bir haneye katılmadın!",
                    discord.Color.red()
                )
                embed.add_field(name="Ne Yapmalıyım?", value="`!başla` komutunu kullan!", inline=False)
                await ctx.send(embed=embed)
                return

            # Get character
            self.db.c.execute('SELECT * FROM asoiaf_characters WHERE user_id = ?', (user_id,))
            character = self.db.c.fetchone()

            house_emoji = get_house_emoji(alliance[1])

            embed = create_embed(
                f"📊 {ctx.author.display_name} DURUMU",
                f"**{house_emoji} {alliance[1]} Hanesi Üyesi**",
                discord.Color.blue()
            )

            # Simple stats
            embed.add_field(name="💰 Altınım", value=f"{alliance[3]:,} altın", inline=True)
            embed.add_field(name="⚔️ Askerlerim", value=f"{alliance[4]:,} asker", inline=True)
            embed.add_field(name="🎭 Karakterim", value=character[1] if character else "Yok", inline=True)

            # Status assessment
            gold = alliance[3]
            soldiers = alliance[4]

            if gold > 10000 and soldiers > 1000:
                status = "🎉 **Çok iyi durumdaşın!**"
                color = discord.Color.green()
            elif gold > 2000 and soldiers > 500:
                status = "👍 **İyi durumdaşın!**"
                color = discord.Color.orange()
            else:
                status = "📈 **Gelişmen gerek!**"
                color = discord.Color.red()

            embed.add_field(name="📊 Genel Durum", value=status, inline=False)
            embed.color = color

            await ctx.send(embed=embed)

        @bot.command(name='kolay_para', aliases=['easy_money', 'para_kazan'])
        async def easy_money(ctx):
            """Easy money making options"""
            user_id = ctx.author.id
            alliance = self.db.get_user_alliance(user_id)

            if not alliance:
                embed = create_embed("❌ Hata", "Önce bir haneye katıl! `!hızlı_hane`", discord.Color.red())
                await ctx.send(embed=embed)
                return

            embed = create_embed(
                "💰 KOLAY PARA KAZANMA YÖNTEMLERİ",
                "**Yeni başlayanlar için basit yöntemler:**",
                discord.Color.gold()
            )

            embed.add_field(
                name="🎲 ŞANS OYUNLARI (HEMEN)",
                value="`!zar 6 3` - Zar at, şanslıysan para kazan!\n"
                      "`!tahmin` - Sayı tahmin et, kazanırsan ödül!",
                inline=False
            )

            embed.add_field(
                name="🏪 KOLAY TİCARET (5 DAKİKA)",
                value="`!ticaret_kolay` - Basit alım-satım\n"
                      "**Garanti kar!**",
                inline=False
            )

            embed.add_field(
                name="🏆 TURNUVA (10 DAKİKA)",
                value="`!turnuvalar` - Katılabileceğin turnuvalar\n"
                      "**Kazanırsan büyük ödül!**",
                inline=False
            )

            embed.add_field(
                name="💼 GÜNLÜK GÖREV (KOLAYCA)",
                value="`!günlük_görev` - Basit görev al\n"
                      "**Her gün garanti para!**",
                inline=False
            )

            embed.set_footer(text="💡 En kolay başlangıç: Zar oyunu!")

            await ctx.send(embed=embed)

        @bot.command(name='ipucu', aliases=['tip', 'hint'])
        async def daily_tip(ctx):
            """Daily helpful tip for users"""
            import random

            tips = [
                "💡 **İpucu:** `!zar` komutuyla şans oyunu oynayarak hızlı para kazanabilirsin!",
                "💡 **İpucu:** Diğer oyuncularla `!evlen` komutuyla evlenerek güç kazanabilirsin!",
                "💡 **İpucu:** `!ticaret_kolay` ile kolay ticaret yaparak para katla!",
                "💡 **İpucu:** `!turnuvalar` komutuna bakarak kolay turnuvalara katıl!",
                "💡 **İpucu:** `!roleplay` ile karakterini canlandırırsan daha eğlenceli olur!",
                "💡 **İpucu:** `!vs` komutuyla arkadaşlarınla karşılaştırma yapabilirsin!",
                "💡 **İpucu:** `!durum` komutuyla ne durumda olduğunu her zaman kontrol edebilirsin!",
                "💡 **İpucu:** `!ne_yapmaliyim` komutu sana her zaman sonraki adımı söyler!",
                "💡 **İpucu:** Para biriktirmek için `!asker_al` komutunu kullanarak güvenliğini artır!",
                "💡 **İpucu:** `!basit_yardım` komutu sadece önemli komutları gösterir!"
            ]

            tip = random.choice(tips)

            embed = create_embed(
                "💡 GÜNLÜK İPUCU",
                tip,
                discord.Color.yellow()
            )

            embed.add_field(
                name="🎯 Daha fazla ipucu istiyorsan",
                value="`!ne_yapmaliyim` - Durumuna özel tavsiye\n"
                      "`!basit_yardım` - Temel komutlar",
                inline=False
            )

            await ctx.send(embed=embed)

        @bot.command(name='altınım', aliases=['my_gold', 'param'])
        async def my_gold(ctx):
            """Quick gold check"""
            user_id = ctx.author.id
            alliance = self.db.get_user_alliance(user_id)

            if not alliance:
                embed = create_embed("❌ Hata", "Önce bir haneye katıl! `!hızlı_hane`", discord.Color.red())
                await ctx.send(embed=embed)
                return

            gold = alliance[3]

            if gold >= 10000:
                status = "🤑 **Zenginsin!**"
                advice = "Artık büyük yatırımlar yapabilirsin!"
                color = discord.Color.gold()
            elif gold >= 2000:
                status = "💰 **İyi durumdaşın!**"
                advice = "Asker alabilir veya yatırım yapabilirsin."
                color = discord.Color.green()
            elif gold >= 500:
                status = "💵 **Orta halli**"
                advice = "Biraz daha para biriktirmeye odaklan."
                color = discord.Color.orange()
            else:
                status = "💸 **Para lazım!**"
                advice = "`!kolay_para` komutunu kullan!"
                color = discord.Color.red()

            embed = create_embed(
                "💰 ALTININ",
                f"**{gold:,} altın** var!",
                color
            )

            embed.add_field(name="📊 Durum", value=status, inline=True)
            embed.add_field(name="💡 Tavsiye", value=advice, inline=True)

            await ctx.send(embed=embed)

        @bot.command(name='askerlerim', aliases=['my_soldiers', 'askerim'])
        async def my_soldiers(ctx):
            """Quick soldier check"""
            user_id = ctx.author.id
            alliance = self.db.get_user_alliance(user_id)

            if not alliance:
                embed = create_embed("❌ Hata", "Önce bir haneye katıl! `!hızlı_hane`", discord.Color.red())
                await ctx.send(embed=embed)
                return

            soldiers = alliance[4]

            if soldiers >= 2000:
                status = "⚔️ **Güçlü ordu!**"
                advice = "Artık savaşa hazırsın!"
                color = discord.Color.red()
            elif soldiers >= 1000:
                status = "🛡️ **İyi savunma**"
                advice = "Daha fazla asker alabilirsin."
                color = discord.Color.orange()
            elif soldiers >= 500:
                status = "👥 **Orta seviye**"
                advice = "Savunma için yeterli ama saldırı zor."
                color = discord.Color.yellow()
            else:
                status = "⚠️ **Zayıf!**"
                advice = "`!asker_al 200` komutuyla asker al!"
                color = discord.Color.red()

            embed = create_embed(
                "⚔️ ASKERLERİM",
                f"**{soldiers:,} asker** var!",
                color
            )

            embed.add_field(name="📊 Durum", value=status, inline=True)
            embed.add_field(name="💡 Tavsiye", value=advice, inline=True)

            await ctx.send(embed=embed)

        logger.info("User friendly commands setup completed")

    async def show_contextual_help(self, ctx, user_action):
        """Show help based on what user is trying to do"""
        help_messages = {
            "join_house": {
                "title": "🏰 Hane Katılma Yardımı",
                "description": "Haneye katılmak çok kolay!",
                "steps": [
                    "`!hızlı_hane` - En iyi haneleri gör",
                    "Beğendiğin hanenin komutunu kopyala",
                    "Örnek: `!katıl Stark`"
                ]
            },
            "get_character": {
                "title": "👤 Karakter Seçme Yardımı",
                "description": "Karakter seçmek de kolay!",
                "steps": [
                    "`!hızlı_karakter` - Popüler karakterleri gör",
                    "Beğendiğin karakterin komutunu kopyala",
                    "Örnek: `!karakter Jon Snow`"
                ]
            },
            "make_money": {
                "title": "💰 Para Kazanma Yardımı",
                "description": "Para kazanmanın kolay yolları!",
                "steps": [
                    "`!zar 6 3` - Şans oyunu oyna",
                    "`!ticaret_kolay` - Basit ticaret yap",
                    "`!günlük_görev` - Günlük görev al"
                ]
            }
        }

        if user_action in help_messages:
            help_data = help_messages[user_action]

            embed = create_embed(
                help_data["title"],
                help_data["description"],
                discord.Color.blue()
            )

            for i, step in enumerate(help_data["steps"], 1):
                embed.add_field(name=f"Adım {i}", value=step, inline=False)

            await ctx.send(embed=embed)