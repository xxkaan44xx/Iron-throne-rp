import discord
import random
import asyncio
import json
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number, get_house_emoji

logger = logging.getLogger(__name__)

class EnhancedEntertainmentSystem:
    def __init__(self, database):
        self.db = database
        
        # Extended riddles database
        self.riddles = [
            {
                "question": "🏰 Winterfell'in kalbinde duran ağacın adı nedir?",
                "answer": ["weirwood", "godswood", "heart tree"],
                "hint": "Tanrıların ormanında bulunur",
                "difficulty": "Kolay",
                "reward": 500
            },
            {
                "question": "⚔️ Valyrian Steel kılıçların kaç tanesi Westeros'ta bilinir?",
                "answer": ["227", "iki yüz yirmi yedi"],
                "hint": "Çok nadir ve değerlidir",
                "difficulty": "Zor",
                "reward": 2000
            },
            {
                "question": "🐉 Daenerys'in en büyük ejderinin adı nedir?",
                "answer": ["drogon"],
                "hint": "Khal Drogo'nun adından gelir",
                "difficulty": "Orta",
                "reward": 1000
            },
            {
                "question": "👑 Iron Throne kaç kılıçtan yapılmıştır?",
                "answer": ["1000", "bin"],
                "hint": "Aegon'un fetih kılıçları",
                "difficulty": "Orta", 
                "reward": 1200
            },
            {
                "question": "🏴‍☠️ Hangi hane 'What is Dead May Never Die' sözünü kullanır?",
                "answer": ["greyjoy"],
                "hint": "Iron Islands'tan gelir",
                "difficulty": "Kolay",
                "reward": 800
            }
        ]
        
        # Trivia categories
        self.trivia_categories = {
            "characters": [
                {"q": "Jon Snow'un gerçek babası kimdir?", "a": ["rhaegar", "rhaegar targaryen"], "r": 1500},
                {"q": "Tyrion Lannister'ın lakabı nedir?", "a": ["imp", "the imp", "cüce"], "r": 800},
                {"q": "Arya Stark'ın kılıç hocası kimdir?", "a": ["syrio", "syrio forel"], "r": 1200},
            ],
            "houses": [
                {"q": "Stark hanesi hangi bölgeyi yönetir?", "a": ["north", "kuzey"], "r": 600},
                {"q": "Lannister'ların sözü nedir?", "a": ["hear me roar"], "r": 800},
                {"q": "Targaryen'ların ejderleri nerede yaşardı?", "a": ["dragonstone"], "r": 1000},
            ],
            "locations": [
                {"q": "King's Landing hangi kıtadadır?", "a": ["westeros"], "r": 400},
                {"q": "The Wall'un yüksekliği kaç feet?", "a": ["700", "yedi yüz"], "r": 1500},
                {"q": "Braavos hangi denizde yer alır?", "a": ["narrow sea"], "r": 1200},
            ]
        }
        
        # Story prompts for creative storytelling
        self.story_prompts = [
            "🏰 Winterfell'de gizemli bir mektup buluyorsun...",
            "🐉 Ejderlerin geri döndüğü gün sen oradaydın...",
            "⚔️ The Wall'da Night Watch'ta görev yaparken...",
            "👑 King's Landing'de Red Keep'te gizli bir toplantı...",
            "🌊 Braavos'ta Faceless Men ile karşılaştın...",
            "🔥 Valyria'nın harabelerinde kayıp bir hazine...",
            "❄️ Beyond the Wall'da White Walker'larla...",
            "💰 Oldtown'da Citadel'de eski bir kitap...",
            "🏹 Dorne'da Red Viper'ın gizli planı...",
            "⚡ Storm's End'de fırtınalı bir gece..."
        ]
        
        # Enhanced character creation
        self.character_traits = {
            "personalities": ["Cesur", "Kurnaz", "Sadık", "Gururlu", "Gizemli", "Komik", "Ciddi", "Romantik"],
            "skills": ["Kılıç Ustası", "Diplomat", "Strateji Uzmanı", "Okçu", "Şövalye", "Tüccar", "Büyücü", "Aşçı"],
            "backgrounds": ["Noble", "Bastard", "Sellsword", "Maester", "Septon", "Merchant", "Assassin", "Bard"],
            "flaws": ["Öfkeli", "Gururlu", "Korkak", "Aç Gözlü", "Güvensiz", "Saf", "Acımasız", "Tembel"]
        }
    
    def setup_entertainment_commands(self, bot):
        """Setup enhanced entertainment commands"""
        
        @bot.command(name='bilmece')
        async def riddle_game(ctx):
            """GoT temalı bilmece oyunu - zeka ve bilgi testi"""
            try:
                riddle = random.choice(self.riddles)
                
                embed = create_embed(
                    "🧩 WESTEROS BİLMECESİ",
                    f"**Zorluk:** {riddle['difficulty']} | **Ödül:** {format_number(riddle['reward'])} altın",
                    discord.Color.purple()
                )
                
                embed.add_field(name="❓ Soru", value=riddle['question'], inline=False)
                embed.add_field(name="💡 İpucu", value=riddle['hint'], inline=False)
                embed.add_field(name="⏰ Süre", value="60 saniye", inline=True)
                embed.add_field(name="📝 Nasıl Cevapla", value="Chat'e cevabını yaz!", inline=True)
                
                await ctx.send(embed=embed)
                
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                try:
                    answer_msg = await bot.wait_for('message', timeout=60.0, check=check)
                    user_answer = answer_msg.content.lower().strip()
                    
                    if any(ans in user_answer for ans in riddle['answer']):
                        # Correct answer
                        alliance = self.db.get_user_alliance(ctx.author.id)
                        if alliance:
                            self.db.update_alliance_resources(alliance[0], riddle['reward'], 0)
                        
                        embed = create_embed(
                            "🎉 DOĞRU CEVAP!",
                            f"Tebrikler {ctx.author.display_name}!",
                            discord.Color.green()
                        )
                        embed.add_field(name="✅ Cevabın", value=answer_msg.content, inline=False)
                        embed.add_field(name="🎁 Ödül", value=f"{format_number(riddle['reward'])} altın", inline=True)
                        embed.add_field(name="🧠 Zeka", value="Three-Eyed Raven seviyesi!", inline=True)
                        
                    else:
                        # Wrong answer
                        embed = create_embed(
                            "❌ YANLIŞ CEVAP",
                            "Maalesef doğru cevap değil!",
                            discord.Color.red()
                        )
                        embed.add_field(name="❌ Cevabın", value=answer_msg.content, inline=False)
                        embed.add_field(name="✅ Doğru Cevap", value=riddle['answer'][0].title(), inline=True)
                        embed.add_field(name="💭 Sonraki Sefere", value="Daha dikkatli ol!", inline=True)
                    
                    await ctx.send(embed=embed)
                    
                except asyncio.TimeoutError:
                    embed = create_embed(
                        "⏰ SÜRE DOLDU!",
                        "60 saniye içinde cevap verilmedi",
                        discord.Color.orange()
                    )
                    embed.add_field(name="✅ Doğru Cevap", value=riddle['answer'][0].title(), inline=True)
                    await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Riddle game error: {e}")
                embed = create_embed("❌ Hata", f"Bilmece hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='trivia')
        async def trivia_contest(ctx, category: str = ""):
            """GoT trivia yarışması - kategoriler: characters, houses, locations"""
            try:
                if not category:
                    embed = create_embed(
                        "🎯 TRIVIA YARIŞMASI",
                        "Bir kategori seç!",
                        discord.Color.blue()
                    )
                    embed.add_field(name="👥 Characters", value="`!trivia characters`", inline=True)
                    embed.add_field(name="🏰 Houses", value="`!trivia houses`", inline=True)
                    embed.add_field(name="🗺️ Locations", value="`!trivia locations`", inline=True)
                    await ctx.send(embed=embed)
                    return
                
                if category.lower() not in self.trivia_categories:
                    embed = create_embed("❌ Hata", "Geçersiz kategori! Kullanılabilir: characters, houses, locations", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                questions = self.trivia_categories[category.lower()]
                question = random.choice(questions)
                
                embed = create_embed(
                    f"🎯 TRIVIA - {category.upper()}",
                    f"**Ödül:** {format_number(question['r'])} altın",
                    discord.Color.gold()
                )
                
                embed.add_field(name="❓ Soru", value=question['q'], inline=False)
                embed.add_field(name="⏰ Süre", value="45 saniye", inline=True)
                
                await ctx.send(embed=embed)
                
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                try:
                    answer_msg = await bot.wait_for('message', timeout=45.0, check=check)
                    user_answer = answer_msg.content.lower().strip()
                    
                    if any(ans in user_answer for ans in question['a']):
                        alliance = self.db.get_user_alliance(ctx.author.id)
                        if alliance:
                            self.db.update_alliance_resources(alliance[0], question['r'], 0)
                        
                        embed = create_embed("🎉 DOĞRU!", "Trivia uzmanısın!", discord.Color.green())
                        embed.add_field(name="🎁 Ödül", value=f"{format_number(question['r'])} altın", inline=True)
                    else:
                        embed = create_embed("❌ Yanlış!", f"Doğru cevap: {question['a'][0]}", discord.Color.red())
                    
                    await ctx.send(embed=embed)
                    
                except asyncio.TimeoutError:
                    embed = create_embed("⏰ Süre Doldu!", f"Doğru cevap: {question['a'][0]}", discord.Color.orange())
                    await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Trivia error: {e}")
                embed = create_embed("❌ Hata", f"Trivia hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='karakter_yarat')
        async def create_character(ctx):
            """Rastgele GoT karakteri oluştur"""
            try:
                houses = ["Stark", "Lannister", "Targaryen", "Baratheon", "Greyjoy", "Tyrell", "Martell", "Arryn", "Tully", "Bolton"]
                
                character = {
                    "name": f"{ctx.author.display_name} {random.choice(['the Bold', 'the Wise', 'the Swift', 'the Strong', 'the Clever'])}",
                    "house": random.choice(houses),
                    "personality": random.choice(self.character_traits["personalities"]),
                    "skill": random.choice(self.character_traits["skills"]),
                    "background": random.choice(self.character_traits["backgrounds"]),
                    "flaw": random.choice(self.character_traits["flaws"]),
                    "age": random.randint(16, 60),
                    "strength": random.randint(1, 10),
                    "intelligence": random.randint(1, 10),
                    "charisma": random.randint(1, 10)
                }
                
                house_emoji = get_house_emoji(character["house"])
                
                embed = create_embed(
                    f"{house_emoji} YENİ KARAKTER",
                    f"**{character['name']}**",
                    discord.Color.from_rgb(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                )
                
                embed.add_field(name="🏰 Hane", value=character['house'], inline=True)
                embed.add_field(name="📅 Yaş", value=character['age'], inline=True) 
                embed.add_field(name="📜 Geçmiş", value=character['background'], inline=True)
                
                embed.add_field(name="😊 Kişilik", value=character['personality'], inline=True)
                embed.add_field(name="⚡ Yetenek", value=character['skill'], inline=True)
                embed.add_field(name="😅 Zayıflık", value=character['flaw'], inline=True)
                
                stats = f"💪 Güç: {character['strength']}/10\n🧠 Zeka: {character['intelligence']}/10\n✨ Karizma: {character['charisma']}/10"
                embed.add_field(name="📊 İstatistikler", value=stats, inline=False)
                
                # Calculate character "value"
                total_stats = character['strength'] + character['intelligence'] + character['charisma']
                embed.add_field(name="🌟 Toplam Güç", value=f"{total_stats}/30", inline=True)
                
                if total_stats >= 25:
                    embed.add_field(name="👑 Rütbe", value="LEGENDARY", inline=True)
                elif total_stats >= 20:
                    embed.add_field(name="🎖️ Rütbe", value="HERO", inline=True)
                elif total_stats >= 15:
                    embed.add_field(name="⚔️ Rütbe", value="WARRIOR", inline=True)
                else:
                    embed.add_field(name="🛡️ Rütbe", value="COMMON", inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Character creation error: {e}")
                embed = create_embed("❌ Hata", f"Karakter yaratma hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='hikaye_başlat')
        async def story_prompt(ctx):
            """Rastgele hikaye başlangıcı al ve devam ettir"""
            try:
                prompt = random.choice(self.story_prompts)
                
                embed = create_embed(
                    "📚 HİKAYE BAŞLANGICI",
                    "Hayal gücünü kullan ve hikayeni yazdır!",
                    discord.Color.from_rgb(138, 43, 226)
                )
                
                embed.add_field(name="📖 Başlangıç", value=prompt, inline=False)
                embed.add_field(name="✍️ Görevin", value="Bu başlangıcı kullanarak kendi hikayeni yaz!", inline=False)
                embed.add_field(name="⏰ Süre", value="5 dakika boyunca yazmaya devam et", inline=True)
                embed.add_field(name="🎁 Ödül", value="Yaratıcılık puanı!", inline=True)
                
                await ctx.send(embed=embed)
                
                # Wait for user's story
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and len(m.content) > 50
                
                try:
                    story_msg = await bot.wait_for('message', timeout=300.0, check=check)  # 5 minutes
                    
                    # Rate the story based on length and creativity
                    story_length = len(story_msg.content)
                    creativity_score = min(10, story_length // 20)  # 1 point per 20 characters, max 10
                    
                    reward = creativity_score * 200  # 200 gold per creativity point
                    
                    alliance = self.db.get_user_alliance(ctx.author.id)
                    if alliance:
                        self.db.update_alliance_resources(alliance[0], reward, 0)
                    
                    embed = create_embed(
                        "📝 HİKAYE TESLİMİ",
                        f"Harika bir hikaye yazdın!",
                        discord.Color.green()
                    )
                    
                    embed.add_field(name="📊 Yaratıcılık Skoru", value=f"{creativity_score}/10", inline=True)
                    embed.add_field(name="📏 Uzunluk", value=f"{story_length} karakter", inline=True)
                    embed.add_field(name="🎁 Ödül", value=f"{format_number(reward)} altın", inline=True)
                    
                    if creativity_score >= 8:
                        embed.add_field(name="🏆 Başarı", value="Mükemmel Hikayeci!", inline=False)
                    elif creativity_score >= 5:
                        embed.add_field(name="✨ Başarı", value="İyi Anlatıcı!", inline=False)
                    else:
                        embed.add_field(name="📚 Tavsiye", value="Daha detaylı yazmayı dene!", inline=False)
                    
                    await ctx.send(embed=embed)
                    
                except asyncio.TimeoutError:
                    embed = create_embed("⏰ Süre Doldu", "Hikaye yazmak için çok geç!", discord.Color.orange())
                    await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Story prompt error: {e}")
                embed = create_embed("❌ Hata", f"Hikaye başlatma hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

logger.info("Enhanced entertainment system initialized successfully")