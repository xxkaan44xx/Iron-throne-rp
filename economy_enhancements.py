import discord
import random
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number, get_house_emoji

logger = logging.getLogger(__name__)

class EconomyEnhancements:
    def __init__(self, database):
        self.db = database
        
        # Market prices for different resources
        self.market_prices = {
            "food": {"base_price": 50, "current": 50, "demand": 1.0},
            "stone": {"base_price": 80, "current": 80, "demand": 1.0},
            "wood": {"base_price": 60, "current": 60, "demand": 1.0},
            "iron": {"base_price": 120, "current": 120, "demand": 1.0},
            "horses": {"base_price": 300, "current": 300, "demand": 1.0},
            "wine": {"base_price": 200, "current": 200, "demand": 1.0}
        }
        
        # Setup market table
        self.setup_market_tables()
    
    def setup_market_tables(self):
        """Create market and trading tables"""
        try:
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS market_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_house_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit INTEGER NOT NULL,
                total_price INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                buyer_house_id INTEGER NULL,
                completed_at TIMESTAMP NULL
            )
            ''')
            
            self.db.c.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_house_id INTEGER NOT NULL,
                buyer_house_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit INTEGER NOT NULL,
                total_price INTEGER NOT NULL,
                trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Market tables created successfully")
        except Exception as e:
            logger.error(f"Error creating market tables: {e}")
    
    def setup_economy_commands(self, bot):
        """Setup enhanced economy commands"""
        
        @bot.command(name='pazar')
        async def market_view(ctx):
            """Kaynak pazarını görüntüle"""
            try:
                embed = create_embed(
                    "🏪 WESTEROS PAZARI",
                    "Güncel kaynak fiyatları ve satış emirleri",
                    discord.Color.gold()
                )
                
                # Show current market prices
                price_text = ""
                for resource, data in self.market_prices.items():
                    trend = "📈" if data['current'] > data['base_price'] else "📉" if data['current'] < data['base_price'] else "➡️"
                    price_text += f"{trend} **{resource.title()}**: {format_number(data['current'])} altın/adet\n"
                
                embed.add_field(name="💰 Güncel Fiyatlar", value=price_text, inline=False)
                
                # Show active market orders
                self.db.c.execute('''
                SELECT mo.resource_type, mo.quantity, mo.price_per_unit, a.name
                FROM market_orders mo
                JOIN alliances a ON mo.seller_house_id = a.id
                WHERE mo.status = 'active'
                ORDER BY mo.price_per_unit ASC
                LIMIT 5
                ''')
                
                orders = self.db.c.fetchall()
                
                if orders:
                    orders_text = ""
                    for resource, quantity, price, house in orders:
                        orders_text += f"🏷️ **{resource.title()}** x{quantity} - {format_number(price)} altın/adet ({house})\n"
                    embed.add_field(name="🛒 Aktif Satış Emirleri", value=orders_text, inline=False)
                else:
                    embed.add_field(name="🛒 Aktif Satış Emirleri", value="Henüz satış emri yok!", inline=False)
                
                embed.add_field(name="📊 Komutlar", 
                              value="`!sat <kaynak> <miktar> <fiyat>` - Kaynak sat\n"
                                    "`!al <kaynak> <miktar>` - Kaynak al\n"
                                    "`!ticaret_geçmişi` - Geçmiş işlemler", 
                              inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Market view error: {e}")
                embed = create_embed("❌ Hata", f"Pazar görüntüleme hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='sat')
        async def sell_resource(ctx, resource_type: str, quantity: int, price_per_unit: int):
            """Pazarda kaynak sat: !sat food 100 55"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Ticaret yapmak için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                alliance_id = alliance[0]
                resource_type = resource_type.lower()
                
                if resource_type not in self.market_prices:
                    embed = create_embed("❌ Hata", f"Geçersiz kaynak! Kullanılabilir: {', '.join(self.market_prices.keys())}", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                if quantity <= 0 or price_per_unit <= 0:
                    embed = create_embed("❌ Hata", "Miktar ve fiyat pozitif olmalı!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Check if house has enough resources (simplified - using gold as proxy)
                alliance_data = self.db.get_alliance_by_id(alliance_id)
                required_gold_equivalent = quantity * 10  # Simplified resource check
                
                if alliance_data[3] < required_gold_equivalent:  # gold field
                    embed = create_embed("❌ Hata", f"Yeterli {resource_type} kaynağın yok!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                total_price = quantity * price_per_unit
                
                # Create market order
                self.db.c.execute('''
                INSERT INTO market_orders (seller_house_id, resource_type, quantity, price_per_unit, total_price)
                VALUES (?, ?, ?, ?, ?)
                ''', (alliance_id, resource_type, quantity, price_per_unit, total_price))
                
                order_id = self.db.c.lastrowid
                self.db.conn.commit()
                
                embed = create_embed(
                    "🏷️ SATIŞ EMRİ OLUŞTURULDU",
                    f"Pazarda satış emrin yerleştirildi!",
                    discord.Color.green()
                )
                
                embed.add_field(name="📦 Kaynak", value=resource_type.title(), inline=True)
                embed.add_field(name="📊 Miktar", value=format_number(quantity), inline=True)
                embed.add_field(name="💰 Birim Fiyat", value=f"{format_number(price_per_unit)} altın", inline=True)
                embed.add_field(name="💎 Toplam Değer", value=f"{format_number(total_price)} altın", inline=True)
                embed.add_field(name="🆔 Emir ID", value=f"#{order_id}", inline=True)
                embed.add_field(name="📈 Pazar Fiyatı", value=f"{format_number(self.market_prices[resource_type]['current'])} altın", inline=True)
                
                # Price comparison
                market_price = self.market_prices[resource_type]['current']
                if price_per_unit < market_price * 0.8:
                    embed.add_field(name="💸 Fiyat Analizi", value="Çok ucuz! Hızla satılabilir", inline=False)
                elif price_per_unit > market_price * 1.2:
                    embed.add_field(name="💰 Fiyat Analizi", value="Pahalı! Satılması zaman alabilir", inline=False)
                else:
                    embed.add_field(name="📊 Fiyat Analizi", value="Makul fiyat! İyi seçim", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Sell resource error: {e}")
                embed = create_embed("❌ Hata", f"Satış hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='al')
        async def buy_resource(ctx, resource_type: str, quantity: int):
            """Pazardan kaynak al: !al food 50"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Ticaret yapmak için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                alliance_id = alliance[0]
                resource_type = resource_type.lower()
                
                if resource_type not in self.market_prices:
                    embed = create_embed("❌ Hata", f"Geçersiz kaynak! Kullanılabilir: {', '.join(self.market_prices.keys())}", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Find cheapest available orders
                self.db.c.execute('''
                SELECT mo.id, mo.seller_house_id, mo.quantity, mo.price_per_unit, a.name
                FROM market_orders mo
                JOIN alliances a ON mo.seller_house_id = a.id
                WHERE mo.resource_type = ? AND mo.status = 'active' AND mo.seller_house_id != ?
                ORDER BY mo.price_per_unit ASC
                ''', (resource_type, alliance_id))
                
                orders = self.db.c.fetchall()
                
                if not orders:
                    embed = create_embed("❌ Stok Yok", f"{resource_type.title()} için aktif satış emri bulunamadı!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Try to fulfill the order
                remaining_quantity = quantity
                total_cost = 0
                successful_purchases = []
                
                for order_id, seller_id, available_qty, price_per_unit, seller_name in orders:
                    if remaining_quantity <= 0:
                        break
                    
                    buy_qty = min(remaining_quantity, available_qty)
                    cost = buy_qty * price_per_unit
                    
                    # Check if buyer has enough gold
                    buyer_data = self.db.get_alliance_by_id(alliance_id)
                    if buyer_data[3] < cost:  # gold field
                        embed = create_embed("❌ Yetersiz Altın", f"Bu satın alma için {format_number(cost)} altın gerekli!", discord.Color.red())
                        await ctx.send(embed=embed)
                        return
                    
                    # Process the purchase
                    # Update buyer's resources
                    self.db.update_alliance_resources(alliance_id, -cost, 0)
                    
                    # Update seller's resources  
                    self.db.update_alliance_resources(seller_id, cost, 0)
                    
                    # Update market order
                    if buy_qty == available_qty:
                        # Complete order
                        self.db.c.execute('''
                        UPDATE market_orders SET status = 'completed', buyer_house_id = ?, completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        ''', (alliance_id, order_id))
                    else:
                        # Partial fulfillment
                        self.db.c.execute('''
                        UPDATE market_orders SET quantity = quantity - ?
                        WHERE id = ?
                        ''', (buy_qty, order_id))
                    
                    # Record trade
                    self.db.c.execute('''
                    INSERT INTO trade_history (seller_house_id, buyer_house_id, resource_type, quantity, price_per_unit, total_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (seller_id, alliance_id, resource_type, buy_qty, price_per_unit, cost))
                    
                    successful_purchases.append({
                        'seller': seller_name,
                        'quantity': buy_qty,
                        'price': price_per_unit,
                        'cost': cost
                    })
                    
                    remaining_quantity -= buy_qty
                    total_cost += cost
                
                self.db.conn.commit()
                
                embed = create_embed(
                    "🛒 SATIN ALMA TAMAMLANDI",
                    f"{resource_type.title()} kaynağı başarıyla satın alındı!",
                    discord.Color.green()
                )
                
                embed.add_field(name="📦 Toplam Alınan", value=f"{quantity - remaining_quantity} {resource_type}", inline=True)
                embed.add_field(name="💰 Toplam Maliyet", value=f"{format_number(total_cost)} altın", inline=True)
                embed.add_field(name="📊 Ortalama Fiyat", value=f"{format_number(total_cost // (quantity - remaining_quantity))} altın/adet", inline=True)
                
                # Show purchase details
                purchase_details = ""
                for purchase in successful_purchases:
                    purchase_details += f"• {purchase['quantity']}x {resource_type} - {purchase['seller']} ({format_number(purchase['price'])} altın/adet)\n"
                
                embed.add_field(name="📋 Satın Alma Detayları", value=purchase_details, inline=False)
                
                if remaining_quantity > 0:
                    embed.add_field(name="⚠️ Uyarı", value=f"{remaining_quantity} adet daha alınamadı (stok yetersiz)", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Buy resource error: {e}")
                embed = create_embed("❌ Hata", f"Satın alma hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='ticaret_geçmişi')
        async def trade_history(ctx):
            """Son ticaret işlemlerini görüntüle"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Ticaret geçmişi görmek için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                alliance_id = alliance[0]
                
                # Get recent trades
                self.db.c.execute('''
                SELECT th.resource_type, th.quantity, th.price_per_unit, th.total_price, th.trade_date,
                       seller.name as seller_name, buyer.name as buyer_name,
                       CASE WHEN th.seller_house_id = ? THEN 'sold' ELSE 'bought' END as trade_type
                FROM trade_history th
                JOIN alliances seller ON th.seller_house_id = seller.id
                JOIN alliances buyer ON th.buyer_house_id = buyer.id
                WHERE th.seller_house_id = ? OR th.buyer_house_id = ?
                ORDER BY th.trade_date DESC
                LIMIT 10
                ''', (alliance_id, alliance_id, alliance_id))
                
                trades = self.db.c.fetchall()
                
                embed = create_embed(
                    "📊 TİCARET GEÇMİŞİ",
                    f"Son 10 ticaret işlemi",
                    discord.Color.blue()
                )
                
                if trades:
                    for trade in trades:
                        resource, qty, price, total, date, seller, buyer, trade_type = trade
                        
                        if trade_type == 'sold':
                            emoji = "💰"
                            partner = buyer
                            action = "sattın"
                        else:
                            emoji = "🛒"
                            partner = seller
                            action = "aldın"
                        
                        trade_date = datetime.fromisoformat(date).strftime("%d/%m %H:%M")
                        
                        embed.add_field(
                            name=f"{emoji} {resource.title()} - {trade_date}",
                            value=f"{qty}x {action} ({partner})\n{format_number(price)} altın/adet - Toplam: {format_number(total)} altın",
                            inline=False
                        )
                else:
                    embed.add_field(name="📝 Sonuç", value="Henüz ticaret işlemi yapılmamış!", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Trade history error: {e}")
                embed = create_embed("❌ Hata", f"Ticaret geçmişi hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)
        
        @bot.command(name='satış_iptal')
        async def cancel_order(ctx, order_id: int):
            """Satış emrini iptal et"""
            try:
                user_id = ctx.author.id
                alliance = self.db.get_user_alliance(user_id)
                
                if not alliance:
                    embed = create_embed("❌ Hata", "Satış emri iptal etmek için bir haneye ait olmalısın!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                alliance_id = alliance[0]
                
                # Check if order exists and belongs to user
                self.db.c.execute('''
                SELECT resource_type, quantity, price_per_unit FROM market_orders
                WHERE id = ? AND seller_house_id = ? AND status = 'active'
                ''', (order_id, alliance_id))
                
                order = self.db.c.fetchone()
                
                if not order:
                    embed = create_embed("❌ Hata", "Bu satış emri bulunamadı veya sana ait değil!", discord.Color.red())
                    await ctx.send(embed=embed)
                    return
                
                # Cancel the order
                self.db.c.execute('''
                UPDATE market_orders SET status = 'cancelled' WHERE id = ?
                ''', (order_id,))
                
                self.db.conn.commit()
                
                resource, quantity, price = order
                
                embed = create_embed(
                    "❌ SATIŞ EMRİ İPTAL EDİLDİ",
                    f"Satış emrin başarıyla iptal edildi!",
                    discord.Color.orange()
                )
                
                embed.add_field(name="🆔 Emir ID", value=f"#{order_id}", inline=True)
                embed.add_field(name="📦 Kaynak", value=resource.title(), inline=True)
                embed.add_field(name="📊 Miktar", value=format_number(quantity), inline=True)
                embed.add_field(name="💰 İptal Edilen Değer", value=f"{format_number(quantity * price)} altın", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Cancel order error: {e}")
                embed = create_embed("❌ Hata", f"Satış iptal hatası: {str(e)}", discord.Color.red())
                await ctx.send(embed=embed)

logger.info("Economy enhancements system initialized successfully")