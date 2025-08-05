
import discord
from utils import create_embed

class TutorialSystem:
    def __init__(self, db):
        self.db = db
        
    async def start_tutorial(self, ctx):
        """Start interactive tutorial for new users"""
        user_id = ctx.author.id
        
        # Check if user already completed tutorial
        self.db.c.execute('SELECT tutorial_completed FROM members WHERE user_id = ?', (user_id,))
        result = self.db.c.fetchone()
        
        if result and result[0]:
            embed = create_embed("📚 Tutorial", "Tutorial'ı zaten tamamlamışsın!", discord.Color.blue())
            await ctx.send(embed=embed)
            return
            
        # Start tutorial
        steps = [
            {
                "title": "🏰 Game of Thrones RP Bot'a Hoşgeldin!",
                "description": "Bu bot ile GoT evreninde roleplay yapabilirsin.",
                "command": "Başlamak için bir haneye katıl: `!haneler`"
            },
            {
                "title": "⚔️ Savaş Sistemi", 
                "description": "Düşman hanelere savaş ilan edebilirsin.",
                "command": "Savaş ilan et: `!savaş_ilan <hane_adı>`"
            },
            {
                "title": "💰 Ekonomi Sistemi",
                "description": "Altın kazan, asker al, gelir kaynakları oluştur.",
                "command": "Durumunu kontrol et: `!hane`"
            }
        ]
        
        for step in steps:
            embed = create_embed(step["title"], step["description"], discord.Color.gold())
            embed.add_field(name="Nasıl Yapılır", value=step["command"], inline=False)
            await ctx.send(embed=embed)
            await asyncio.sleep(2)
            
        # Mark tutorial as completed
        self.db.c.execute('UPDATE members SET tutorial_completed = 1 WHERE user_id = ?', (user_id,))
        self.db.conn.commit()
