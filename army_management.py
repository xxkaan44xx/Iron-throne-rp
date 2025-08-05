
import logging
from datetime import datetime, timedelta
from utils import format_number, create_embed, get_house_emoji
import random
import discord

logger = logging.getLogger(__name__)

class ArmyManagement:
    def __init__(self, database):
        self.db = database
        
        # Army upgrade costs (based on current level)
        self.upgrade_costs = {
            'weapons_quality': lambda level: int(5000 * (1.5 ** (level / 10))),
            'armor_quality': lambda level: int(4000 * (1.5 ** (level / 10))),
            'army_training': lambda level: int(3000 * (1.5 ** (level / 10))),
            'siege_weapons': lambda level: int(10000 * (1.2 ** level)),
            'cavalry': lambda level: int(500 * level),
            'archers': lambda level: int(300 * level),
            'navy_ships': lambda level: int(15000 * level)
        }
        
        # Resource costs for army maintenance (per soldier per day)
        self.maintenance_costs = {
            'food': 2,
            'iron': 0.1,
            'wood': 0.05
        }

    def get_army_status(self, house_id):
        """Get complete army status for a house"""
        try:
            # Get alliance data
            alliance = self.db.get_alliance_by_id(house_id)
            if not alliance:
                return None
            
            # Get army resources
            self.db.c.execute('SELECT * FROM army_resources WHERE house_id = ?', (house_id,))
            army_data = self.db.c.fetchone()
            
            # Get house resources
            self.db.c.execute('SELECT resource_type, quantity, quality FROM house_resources WHERE house_id = ?', (house_id,))
            resources = {row[0]: {'quantity': row[1], 'quality': row[2]} for row in self.db.c.fetchall()}
            
            if not army_data:
                # Initialize army resources if they don't exist
                self.db.c.execute('''
                INSERT INTO army_resources (house_id, food_supplies, weapons_quality, armor_quality, 
                                          siege_weapons, cavalry, archers, infantry, navy_ships, 
                                          army_training, morale)
                VALUES (?, 1000, 50, 50, 0, 0, 0, ?, 0, 50, 70)
                ''', (house_id, alliance[4]))  # infantry = total soldiers
                self.db.conn.commit()
                return self.get_army_status(house_id)
            
            # Calculate army effectiveness
            effectiveness = self._calculate_army_effectiveness(army_data, alliance[4])
            
            return {
                'alliance': alliance,
                'army_data': army_data,
                'resources': resources,
                'effectiveness': effectiveness,
                'daily_maintenance': self._calculate_daily_maintenance(alliance[4])
            }
            
        except Exception as e:
            logger.error(f"Error getting army status: {e}")
            return None

    def _calculate_army_effectiveness(self, army_data, total_soldiers):
        """Calculate overall army effectiveness (0-100)"""
        if total_soldiers == 0:
            return 0
        
        # Weighted factors for army effectiveness
        weapons_factor = (army_data[2] or 50) * 0.25  # weapons_quality
        armor_factor = (army_data[3] or 50) * 0.20    # armor_quality
        training_factor = (army_data[9] or 50) * 0.25  # army_training
        morale_factor = (army_data[10] or 70) * 0.15   # morale
        supply_factor = min(100, (army_data[1] or 1000) / (total_soldiers * 2)) * 0.15  # food_supplies
        
        effectiveness = weapons_factor + armor_factor + training_factor + morale_factor + supply_factor
        return min(100, max(0, int(effectiveness)))

    def _calculate_daily_maintenance(self, soldier_count):
        """Calculate daily resource maintenance costs"""
        return {
            'food': soldier_count * self.maintenance_costs['food'],
            'iron': int(soldier_count * self.maintenance_costs['iron']),
            'wood': int(soldier_count * self.maintenance_costs['wood'])
        }

    def upgrade_army_component(self, house_id, component, levels=1):
        """Upgrade a specific army component"""
        try:
            army_status = self.get_army_status(house_id)
            if not army_status:
                return False, "Ordu bilgileri alınamadı!"
            
            alliance = army_status['alliance']
            army_data = army_status['army_data']
            
            # Component mapping
            component_map = {
                'silah': ('weapons_quality', 2, 100),
                'zırh': ('armor_quality', 3, 100),
                'eğitim': ('army_training', 9, 100),
                'kuşatma': ('siege_weapons', 4, alliance[4] // 10),  # Max 1 siege weapon per 10 soldiers
                'süvari': ('cavalry', 5, alliance[4] // 2),          # Max 50% cavalry
                'okçu': ('archers', 6, alliance[4] // 2),            # Max 50% archers
                'donanma': ('navy_ships', 8, 200)                   # Max 200 ships
            }
            
            if component not in component_map:
                return False, f"Geçersiz bileşen! Kullanılabilir: {', '.join(component_map.keys())}"
            
            db_field, field_index, max_value = component_map[component]
            current_value = army_data[field_index] or 0
            new_value = current_value + levels
            
            if new_value > max_value:
                return False, f"Maksimum seviye: {max_value}. Mevcut: {current_value}"
            
            # Calculate cost
            total_cost = 0
            for i in range(levels):
                level_cost = self.upgrade_costs[db_field](current_value + i)
                total_cost += level_cost
            
            if alliance[3] < total_cost:  # gold check
                return False, f"Yetersiz altın! Gerekli: {format_number(total_cost)}, Mevcut: {format_number(alliance[3])}"
            
            # Perform upgrade
            self.db.c.execute(f'UPDATE army_resources SET {db_field} = ? WHERE house_id = ?', 
                            (new_value, house_id))
            self.db.update_alliance_resources(house_id, -total_cost, 0)
            self.db.conn.commit()
            
            component_names = {
                'silah': 'Silah Kalitesi',
                'zırh': 'Zırh Kalitesi', 
                'eğitim': 'Ordu Eğitimi',
                'kuşatma': 'Kuşatma Silahları',
                'süvari': 'Süvari Birliği',
                'okçu': 'Okçu Birliği',
                'donanma': 'Donanma Gemileri'
            }
            
            return True, f"{component_names[component]} {current_value} → {new_value} seviyesine yükseltildi! Maliyet: {format_number(total_cost)} altın"
            
        except Exception as e:
            logger.error(f"Error upgrading army component: {e}")
            return False, f"Yükseltme hatası: {str(e)}"

    def buy_resources(self, house_id, resource_type, quantity):
        """Buy resources for army maintenance"""
        try:
            alliance = self.db.get_alliance_by_id(house_id)
            if not alliance:
                return False, "Hane bulunamadı!"
            
            # Resource prices (per unit)
            prices = {
                'food': 5,
                'stone': 10,
                'wood': 8,
                'iron': 15,
                'horses': 100,
                'wine': 20
            }
            
            if resource_type not in prices:
                return False, f"Geçersiz kaynak! Kullanılabilir: {', '.join(prices.keys())}"
            
            total_cost = quantity * prices[resource_type]
            
            if alliance[3] < total_cost:
                return False, f"Yetersiz altın! Gerekli: {format_number(total_cost)}, Mevcut: {format_number(alliance[3])}"
            
            # Add resource
            self.db.c.execute('''
            INSERT OR REPLACE INTO house_resources (house_id, resource_type, quantity, quality)
            VALUES (?, ?, COALESCE((SELECT quantity FROM house_resources WHERE house_id = ? AND resource_type = ?), 0) + ?, 60)
            ''', (house_id, resource_type, house_id, resource_type, quantity))
            
            self.db.update_alliance_resources(house_id, -total_cost, 0)
            self.db.conn.commit()
            
            return True, f"{format_number(quantity)} {resource_type} satın alındı! Maliyet: {format_number(total_cost)} altın"
            
        except Exception as e:
            logger.error(f"Error buying resources: {e}")
            return False, f"Kaynak satın alma hatası: {str(e)}"

    def set_army_composition(self, house_id, infantry=None, cavalry=None, archers=None, siege=None):
        """Admin function to set army composition"""
        try:
            alliance = self.db.get_alliance_by_id(house_id)
            if not alliance:
                return False, "Hane bulunamadı!"
            
            total_soldiers = alliance[4]
            updates = []
            values = []
            
            if infantry is not None:
                updates.append("infantry = ?")
                values.append(min(infantry, total_soldiers))
            
            if cavalry is not None:
                updates.append("cavalry = ?")
                values.append(min(cavalry, total_soldiers // 2))
            
            if archers is not None:
                updates.append("archers = ?")
                values.append(min(archers, total_soldiers // 2))
            
            if siege is not None:
                updates.append("siege_weapons = ?")
                values.append(min(siege, total_soldiers // 10))
            
            if not updates:
                return False, "Hiç güncelleme belirtilmedi!"
            
            values.append(house_id)
            query = f"UPDATE army_resources SET {', '.join(updates)} WHERE house_id = ?"
            self.db.c.execute(query, values)
            self.db.conn.commit()
            
            return True, "Ordu kompozisyonu güncellendi!"
            
        except Exception as e:
            logger.error(f"Error setting army composition: {e}")
            return False, f"Ordu kompozisyonu ayarlama hatası: {str(e)}"

    def create_army_embed(self, army_status):
        """Create Discord embed for army status"""
        if not army_status:
            return create_embed("❌ Hata", "Ordu bilgileri alınamadı!", discord.Color.red())
        
        alliance = army_status['alliance']
        army_data = army_status['army_data']
        resources = army_status['resources']
        effectiveness = army_status['effectiveness']
        
        house_emoji = get_house_emoji(alliance[1])
        
        # Effectiveness color
        if effectiveness >= 80:
            color = discord.Color.green()
        elif effectiveness >= 60:
            color = discord.Color.gold()
        elif effectiveness >= 40:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()
        
        embed = create_embed(f"{house_emoji} {alliance[1]} Ordu Durumu", 
                           f"Genel Etkinlik: **{effectiveness}%**", 
                           color)
        
        # Army composition
        total_assigned = (army_data[7] or 0) + (army_data[5] or 0) + (army_data[6] or 0)  # infantry + cavalry + archers
        unassigned = max(0, alliance[4] - total_assigned)
        
        embed.add_field(
            name="⚔️ Ordu Kompozisyonu",
            value=f"👥 **Toplam Asker:** {format_number(alliance[4])}\n"
                  f"🏃 **Piyade:** {format_number(army_data[7] or 0)}\n"
                  f"🐎 **Süvari:** {format_number(army_data[5] or 0)}\n"
                  f"🏹 **Okçu:** {format_number(army_data[6] or 0)}\n"
                  f"📦 **Atanmamış:** {format_number(unassigned)}",
            inline=True
        )
        
        # Equipment and training
        embed.add_field(
            name="🛡️ Donanım & Eğitim",
            value=f"⚔️ **Silah Kalitesi:** {army_data[2] or 50}%\n"
                  f"🛡️ **Zırh Kalitesi:** {army_data[3] or 50}%\n"
                  f"🎯 **Eğitim Seviyesi:** {army_data[9] or 50}%\n"
                  f"💪 **Moral:** {army_data[10] or 70}%\n"
                  f"🏰 **Kuşatma Silahı:** {army_data[4] or 0}",
            inline=True
        )
        
        # Resources
        food_qty = resources.get('food', {}).get('quantity', 0)
        iron_qty = resources.get('iron', {}).get('quantity', 0)
        wood_qty = resources.get('wood', {}).get('quantity', 0)
        
        embed.add_field(
            name="📦 Kaynaklar",
            value=f"🍖 **Yiyecek:** {format_number(food_qty)}\n"
                  f"⚙️ **Demir:** {format_number(iron_qty)}\n"
                  f"🪵 **Ahşap:** {format_number(wood_qty)}\n"
                  f"🐎 **At:** {format_number(resources.get('horses', {}).get('quantity', 0))}\n"
                  f"🍷 **Şarap:** {format_number(resources.get('wine', {}).get('quantity', 0))}",
            inline=True
        )
        
        # Navy (if applicable)
        if army_data[8] and army_data[8] > 0:
            embed.add_field(
                name="⚓ Donanma",
                value=f"🚢 **Gemi Sayısı:** {army_data[8]}\n"
                      f"👨‍✈️ **Deniz Gücü:** {min(100, army_data[8] * 5)}%",
                inline=True
            )
        
        # Daily maintenance
        maintenance = army_status['daily_maintenance']
        embed.add_field(
            name="📊 Günlük İhtiyaç",
            value=f"🍖 {format_number(maintenance['food'])} yiyecek\n"
                  f"⚙️ {format_number(maintenance['iron'])} demir\n"
                  f"🪵 {format_number(maintenance['wood'])} ahşap",
            inline=True
        )
        
        embed.set_footer(text="!ordu_yükselt <bileşen> <seviye> ile geliştir | !kaynak_al <tür> <miktar> ile kaynak satın al")
        
        return embed
