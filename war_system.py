import random
import asyncio
import discord
import logging
from datetime import datetime, timedelta
from utils import create_embed, format_number, get_house_emoji, get_weather_emoji, get_terrain_emoji, get_random_battle_flavor_text

logger = logging.getLogger(__name__)

class WarSystem:
    def __init__(self, database):
        self.db = database
        
        # Battle actions with effects
        self.battle_actions = {
            "saldır": {"damage_multiplier": 1.2, "defense_multiplier": 0.8, "description": "Agresif saldırı"},
            "savun": {"damage_multiplier": 0.7, "defense_multiplier": 1.5, "description": "Savunma pozisyonu"},
            "maneuvra": {"damage_multiplier": 1.0, "defense_multiplier": 1.0, "description": "Taktiksel hareket"},
            "geri_çekil": {"damage_multiplier": 0.5, "defense_multiplier": 1.8, "description": "Stratejik geri çekilme"},
            "taarruz": {"damage_multiplier": 1.5, "defense_multiplier": 0.5, "description": "Topyekün saldırı"}
        }
        
        # Weather effects
        self.weather_effects = {
            "normal": {"attack_mod": 1.0, "defense_mod": 1.0, "description": "Normal hava"},
            "yağmur": {"attack_mod": 0.8, "defense_mod": 1.1, "description": "Yağmurlu hava"},
            "kar": {"attack_mod": 0.7, "defense_mod": 1.2, "description": "Karlı hava"},
            "fırtına": {"attack_mod": 0.6, "defense_mod": 1.3, "description": "Fırtınalı hava"},
            "sis": {"attack_mod": 0.9, "defense_mod": 0.9, "description": "Sisli hava"}
        }
        
        # Terrain effects
        self.terrain_effects = {
            "ova": {"attack_mod": 1.1, "defense_mod": 0.9, "description": "Ova arazi"},
            "orman": {"attack_mod": 0.9, "defense_mod": 1.1, "description": "Ormanlık arazi"},
            "dağ": {"attack_mod": 0.8, "defense_mod": 1.3, "description": "Dağlık arazi"},
            "sahil": {"attack_mod": 1.0, "defense_mod": 1.0, "description": "Sahil arazi"},
            "çöl": {"attack_mod": 0.9, "defense_mod": 0.8, "description": "Çöl arazi"}
        }

    def can_declare_war(self, attacker_id, defender_id, battle_size="orta"):
        """Check if war can be declared"""
        try:
            # Check if same alliance
            if attacker_id == defender_id:
                return False, "Kendi hanene savaş ilan edemezsin!"
            
            # Check if already at war
            existing_wars = self.db.get_active_wars()
            for war in existing_wars:
                if ((war[1] == attacker_id and war[2] == defender_id) or 
                    (war[1] == defender_id and war[2] == attacker_id)):
                    return False, "Bu hanelerle zaten aktif bir savaş var!"
            
            # Check if attacker has enough soldiers
            attacker = self.db.get_alliance_by_id(attacker_id)
            if not attacker or attacker[4] < 100:  # soldiers field
                return False, "Savaş ilan etmek için en az 100 askerin olmalı!"
            
            # Check if defender exists and has soldiers
            defender = self.db.get_alliance_by_id(defender_id)
            if not defender:
                return False, "Hedef hane bulunamadı!"
            
            if defender[4] < 50:  # soldiers field
                return False, "Hedef hanenin yeterli askeri yok!"
            
            # Battle size requirements
            battle_sizes = {
                "küçük": {"min_soldiers": 100, "max_ratio": 0.3, "description": "Küçük çaplı çatışma"},
                "orta": {"min_soldiers": 500, "max_ratio": 0.6, "description": "Orta büyüklükte muharebe"},
                "büyük": {"min_soldiers": 1000, "max_ratio": 0.8, "description": "Büyük savaş"},
                "topyekün": {"min_soldiers": 2000, "max_ratio": 1.0, "description": "Topyekün savaş"}
            }
            
            if battle_size not in battle_sizes:
                return False, "Geçersiz muharebe büyüklüğü! (küçük/orta/büyük/topyekün)"
            
            size_info = battle_sizes[battle_size]
            if attacker[4] < size_info["min_soldiers"] or defender[4] < size_info["min_soldiers"]:
                return False, f"{size_info['description']} için en az {size_info['min_soldiers']} askere ihtiyaç var!"
            
            return True, f"{size_info['description']} ilan edilebilir!"
            
        except Exception as e:
            logger.error(f"Error checking war declaration: {e}")
            return False, "Savaş kontrolü sırasında hata oluştu!"

    async def execute_battle_turn(self, war_id, attacker_action, defender_action):
        """Execute a battle turn between two armies"""
        try:
            # Get war data
            self.db.c.execute('SELECT * FROM wars WHERE id = ? AND status = "active"', (war_id,))
            war = self.db.c.fetchone()
            
            if not war:
                return None, "Savaş bulunamadı veya bitmiş!"
            
            # Get alliance data
            attacker = self.db.get_alliance_by_id(war[1])
            defender = self.db.get_alliance_by_id(war[2])
            
            if not attacker or not defender:
                return None, "Hane verileri alınamadı!"
            
            # Get current turn number
            self.db.c.execute('SELECT COUNT(*) FROM battle_logs WHERE war_id = ?', (war_id,))
            turn_number = self.db.c.fetchone()[0] + 1
            
            # Calculate battle effects
            weather_effect = self.weather_effects.get(war[8], self.weather_effects["normal"])
            terrain_effect = self.terrain_effects.get(war[9], self.terrain_effects["ova"])
            
            # Get action effects
            att_action_effect = self.battle_actions.get(attacker_action, self.battle_actions["saldır"])
            def_action_effect = self.battle_actions.get(defender_action, self.battle_actions["savun"])
            
            # Calculate remaining soldiers
            att_soldiers = max(0, attacker[4] - war[4])  # Total soldiers - losses
            def_soldiers = max(0, defender[4] - war[5])
            
            # Check if war should end due to no soldiers
            if att_soldiers <= 0:
                await self._end_war_no_soldiers(war_id, defender[0], attacker, defender)
                return self._create_war_end_report(war_id, turn_number, attacker, defender, defender[0], "Saldıran tarafın askeri kalmadı!"), None
            
            if def_soldiers <= 0:
                await self._end_war_no_soldiers(war_id, attacker[0], attacker, defender)
                return self._create_war_end_report(war_id, turn_number, attacker, defender, attacker[0], "Savunan tarafın askeri kalmadı!"), None
            
            # Apply house special abilities and calculate combat power
            att_power = self._calculate_combat_power(attacker, att_soldiers, att_action_effect, weather_effect, terrain_effect, True)
            def_power = self._calculate_combat_power(defender, def_soldiers, def_action_effect, weather_effect, terrain_effect, False)
            
            # Add randomness to combat
            att_power *= random.uniform(0.8, 1.2)
            def_power *= random.uniform(0.8, 1.2)
            
            # Determine casualties based on combat power difference
            power_ratio = att_power / max(def_power, 1)
            
            # Calculate casualties
            base_casualty_rate = 0.05  # 5% base casualty rate
            if power_ratio > 1.5:
                att_casualty_rate = base_casualty_rate * 0.5
                def_casualty_rate = base_casualty_rate * 1.5
            elif power_ratio > 1.2:
                att_casualty_rate = base_casualty_rate * 0.7
                def_casualty_rate = base_casualty_rate * 1.3
            elif power_ratio > 0.8:
                att_casualty_rate = base_casualty_rate
                def_casualty_rate = base_casualty_rate
            elif power_ratio > 0.5:
                att_casualty_rate = base_casualty_rate * 1.3
                def_casualty_rate = base_casualty_rate * 0.7
            else:
                att_casualty_rate = base_casualty_rate * 1.5
                def_casualty_rate = base_casualty_rate * 0.5
            
            att_casualties = int(att_soldiers * att_casualty_rate * random.uniform(0.5, 1.5))
            def_casualties = int(def_soldiers * def_casualty_rate * random.uniform(0.5, 1.5))
            
            # Ensure realistic casualty limits
            att_casualties = max(0, min(att_casualties, att_soldiers // 5))  # Max 20% per turn
            def_casualties = max(0, min(def_casualties, def_soldiers // 5))
            
            # Update war losses
            new_att_losses = war[4] + att_casualties
            new_def_losses = war[5] + def_casualties
            
            self.db.c.execute('''
            UPDATE wars SET attacker_losses = ?, defender_losses = ?
            WHERE id = ?
            ''', (new_att_losses, new_def_losses, war_id))
            
            # Determine battle result
            battle_result = self._determine_battle_result(att_power, def_power)
            result_text = self._get_battle_result_text(battle_result)
            
            # Add flavor text
            flavor_text = get_random_battle_flavor_text(battle_result)
            result = f"{result_text}\n*{flavor_text}*"
            
            # Add battle log
            self.db.add_battle_log(war_id, turn_number, attacker_action, defender_action, 
                                  result, att_casualties, def_casualties)
            
            # Check for war end conditions
            remaining_att = att_soldiers - att_casualties
            remaining_def = def_soldiers - def_casualties
            
            winner = None
            end_reason = ""
            
            # Check victory conditions
            if remaining_att <= attacker[4] * 0.1:  # Less than 10% soldiers left
                winner = defender[0]
                end_reason = f"🏆 **{defender[1]}** hanesi savaşı kazandı! Düşman ordusunu yok etti!"
            elif remaining_def <= defender[4] * 0.1:
                winner = attacker[0]
                end_reason = f"🏆 **{attacker[1]}** hanesi savaşı kazandı! Düşman ordusunu yok etti!"
            elif turn_number >= 50:  # Max 50 turns
                winner = -1  # Draw
                end_reason = "⏱️ Savaş çok uzun sürdü ve berabere bitti!"
            
            if winner is not None:
                self.db.end_war(war_id, winner if winner != -1 else None)
                await self._apply_war_consequences(war_id, attacker, defender, winner)
                result += f"\n\n{end_reason}"
            
            self.db.conn.commit()
            
            # Create battle report
            battle_report = {
                "war_id": war_id,
                "turn": turn_number,
                "attacker": attacker[1],
                "defender": defender[1],
                "attacker_action": attacker_action,
                "defender_action": defender_action,
                "attacker_casualties": att_casualties,
                "defender_casualties": def_casualties,
                "attacker_remaining": remaining_att,
                "defender_remaining": remaining_def,
                "result": result,
                "battle_result": battle_result,
                "war_ended": winner is not None,
                "winner": winner,
                "weather": war[8],
                "terrain": war[9]
            }
            
            return battle_report, None
            
        except Exception as e:
            logger.error(f"Error executing battle turn: {e}")
            return None, f"Savaş turu işlenirken hata oluştu: {str(e)}"

    def _calculate_combat_power(self, alliance, soldiers, action_effect, weather_effect, terrain_effect, is_attacker, battle_size="orta"):
        """Calculate combat power for an alliance"""
        # Battle size modifiers
        size_modifiers = {
            "küçük": {"soldiers_ratio": 0.3, "intensity": 0.8},
            "orta": {"soldiers_ratio": 0.6, "intensity": 1.0},
            "büyük": {"soldiers_ratio": 0.8, "intensity": 1.2},
            "topyekün": {"soldiers_ratio": 1.0, "intensity": 1.5}
        }
        
        size_info = size_modifiers.get(battle_size, size_modifiers["orta"])
        effective_soldiers = int(soldiers * size_info["soldiers_ratio"])
        base_power = effective_soldiers * 10 * size_info["intensity"]
        
        # Apply action modifiers
        if is_attacker:
            base_power *= action_effect["damage_multiplier"]
        else:
            base_power *= action_effect["defense_multiplier"]
        
        # Apply weather effects
        if is_attacker:
            base_power *= weather_effect["attack_mod"]
        else:
            base_power *= weather_effect["defense_mod"]
        
        # Apply terrain effects
        if is_attacker:
            base_power *= terrain_effect["attack_mod"]
        else:
            base_power *= terrain_effect["defense_mod"]
        
        # Apply house special abilities
        house_name = alliance[1]
        if house_name == "Stark":
            if not is_attacker:  # Defensive bonus
                base_power *= 1.25
            # Winter/cold weather bonus
            if weather_effect.get("description", "").find("kar") != -1:
                base_power *= 1.15
        elif house_name == "Lannister":  # Gold advantage
            base_power *= 1.15
        elif house_name == "Targaryen":  # Dragon heritage
            base_power *= 1.2
            # Fire advantage (bonus against certain houses)
        elif house_name == "Baratheon" and is_attacker:  # Fury in attack
            base_power *= 1.3
        elif house_name == "Tyrell":  # Numbers advantage
            base_power *= 1.2
        elif house_name == "Martell":  # Desert/guerrilla tactics
            base_power *= 1.1
            if terrain_effect.get("description", "").find("çöl") != -1:
                base_power *= 1.2
        
        return int(base_power)

    def _determine_battle_result(self, att_power, def_power):
        """Determine battle result based on power comparison"""
        ratio = att_power / max(def_power, 1)
        
        if ratio > 1.5:
            return "attacker_major"
        elif ratio > 1.1:
            return "attacker_minor"
        elif ratio < 0.67:
            return "defender_major"
        elif ratio < 0.9:
            return "defender_minor"
        else:
            return "draw"

    def _get_battle_result_text(self, battle_result):
        """Get battle result description"""
        result_texts = {
            "attacker_major": "Saldıran taraf büyük zafer kazandı!",
            "attacker_minor": "Saldıran taraf zafer kazandı!",
            "defender_major": "Savunan taraf büyük zafer kazandı!",
            "defender_minor": "Savunan taraf zafer kazandı!",
            "draw": "Berabere! Her iki taraf da kayıp verdi."
        }
        return result_texts.get(battle_result, "Savaş devam ediyor.")

    async def _end_war_no_soldiers(self, war_id, winner_id, attacker, defender):
        """End war when one side has no soldiers left"""
        self.db.end_war(war_id, winner_id)
        await self._apply_war_consequences(war_id, attacker, defender, winner_id)

    def _create_war_end_report(self, war_id, turn_number, attacker, defender, winner_id, reason):
        """Create a war end report"""
        return {
            "war_id": war_id,
            "turn": turn_number,
            "attacker": attacker[1],
            "defender": defender[1],
            "attacker_action": "none",
            "defender_action": "none",
            "attacker_casualties": 0,
            "defender_casualties": 0,
            "attacker_remaining": 0 if winner_id == defender[0] else attacker[4],
            "defender_remaining": 0 if winner_id == attacker[0] else defender[4],
            "result": reason,
            "battle_result": "ended",
            "war_ended": True,
            "winner": winner_id,
            "weather": "normal",
            "terrain": "ova"
        }

    async def _apply_war_consequences(self, war_id, attacker, defender, winner_id):
        """Apply consequences of war end"""
        try:
            if winner_id == attacker[0]:  # Attacker wins
                # Attacker gains resources
                gold_gain = max(100, defender[3] // 4)  # 25% of defender's gold, minimum 100
                soldiers_gain = min(1000, max(50, defender[4] // 10))  # 10% of defender's soldiers or max 1000
                
                self.db.update_alliance_resources(attacker[0], gold_gain, soldiers_gain)
                self.db.update_alliance_resources(defender[0], -min(gold_gain, defender[3] // 2), -soldiers_gain)
                
                # Seize income sources
                defender_sources = self.db.get_income_sources(defender[0])
                sources_to_seize = min(2, len([s for s in defender_sources if not s[9]]))  # Max 2 non-seized sources
                
                unseized_sources = [s for s in defender_sources if not s[9]][:sources_to_seize]
                for source in unseized_sources:
                    self.db.c.execute('''
                    UPDATE income_sources SET seized = 1, seized_by = ?
                    WHERE id = ?
                    ''', (attacker[0], source[0]))
                
            elif winner_id == defender[0]:  # Defender wins
                # Defender gets smaller rewards for successful defense
                gold_gain = max(50, attacker[3] // 8)  # 12.5% of attacker's gold, minimum 50
                
                self.db.update_alliance_resources(defender[0], gold_gain, 0)
                self.db.update_alliance_resources(attacker[0], -min(gold_gain, attacker[3] // 3), 0)
            
            self.db.conn.commit()
            
        except Exception as e:
            logger.error(f"Error applying war consequences: {e}")

    def create_battle_embed(self, battle_report):
        """Create a Discord embed for battle results"""
        try:
            att_emoji = get_house_emoji(battle_report["attacker"])
            def_emoji = get_house_emoji(battle_report["defender"])
            weather_emoji = get_weather_emoji(battle_report.get("weather", "normal"))
            terrain_emoji = get_terrain_emoji(battle_report.get("terrain", "ova"))
            
            if battle_report["war_ended"]:
                title = "🏆 Savaş Sona Erdi!"
                color = discord.Color.gold()
            else:
                title = f"⚔️ Savaş Turu #{battle_report['turn']}"
                color = discord.Color.red()
            
            embed = create_embed(title, battle_report["result"], color)
            
            # Battle participants
            embed.add_field(
                name=f"{att_emoji} {battle_report['attacker']} (Saldıran)",
                value=f"**Aksiyon:** {battle_report['attacker_action'].title()}\n"
                      f"**Kayıp:** {format_number(battle_report['attacker_casualties'])} asker\n"
                      f"**Kalan:** {format_number(battle_report['attacker_remaining'])} asker",
                inline=True
            )
            
            embed.add_field(
                name=f"{def_emoji} {battle_report['defender']} (Savunan)",
                value=f"**Aksiyon:** {battle_report['defender_action'].title()}\n"
                      f"**Kayıp:** {format_number(battle_report['defender_casualties'])} asker\n"
                      f"**Kalan:** {format_number(battle_report['defender_remaining'])} asker",
                inline=True
            )
            
            # Battle conditions
            embed.add_field(
                name="🌤️ Savaş Koşulları",
                value=f"{weather_emoji} Hava: {battle_report.get('weather', 'normal').title()}\n"
                      f"{terrain_emoji} Arazi: {battle_report.get('terrain', 'ova').title()}",
                inline=True
            )
            
            # Battle info
            embed.add_field(name="🆔 Savaş ID", value=str(battle_report["war_id"]), inline=True)
            embed.add_field(name="🔄 Tur", value=str(battle_report["turn"]), inline=True)
            embed.add_field(name="📊 Sonuç", value=battle_report["battle_result"].replace("_", " ").title(), inline=True)
            
            if not battle_report["war_ended"]:
                embed.add_field(
                    name="📋 Sıradaki Turda",
                    value="Her iki taraf da aksiyonlarını seçsin:\n"
                          "`!saldır <savaş_id>`, `!savun <savaş_id>`, `!maneuvra <savaş_id>`, `!geri_çekil <savaş_id>`, `!taarruz <savaş_id>`",
                    inline=False
                )
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating battle embed: {e}")
            return create_embed("❌ Hata", "Savaş raporu oluşturulamadı!", discord.Color.red())

    def get_war_status(self, war_id):
        """Get detailed war status"""
        try:
            self.db.c.execute('''
            SELECT w.*, a1.name as attacker_name, a2.name as defender_name 
            FROM wars w
            JOIN alliances a1 ON w.attacker_id = a1.id
            JOIN alliances a2 ON w.defender_id = a2.id
            WHERE w.id = ?
            ''', (war_id,))
            
            war_data = self.db.c.fetchone()
            if not war_data:
                return None
            
            # Get battle logs
            self.db.c.execute('''
            SELECT turn_number, attacker_action, defender_action, result, 
                   attacker_damage, defender_damage, timestamp
            FROM battle_logs 
            WHERE war_id = ?
            ORDER BY turn_number DESC
            LIMIT 10
            ''', (war_id,))
            
            recent_battles = self.db.c.fetchall()
            
            return {
                "war": war_data,
                "recent_battles": recent_battles
            }
            
        except Exception as e:
            logger.error(f"Error getting war status: {e}")
            return None

    def create_war_status_embed(self, war_status):
        """Create embed for war status display"""
        if not war_status:
            return create_embed("❌ Hata", "Savaş bilgileri alınamadı!", discord.Color.red())
        
        war = war_status["war"]
        battles = war_status["recent_battles"]
        
        att_emoji = get_house_emoji(war[11])  # attacker_name
        def_emoji = get_house_emoji(war[12])  # defender_name
        weather_emoji = get_weather_emoji(war[8])
        terrain_emoji = get_terrain_emoji(war[9])
        
        title = f"⚔️ Savaş #{war[0]} - {war[3].title()}"
        description = f"{att_emoji} **{war[11]}** vs {def_emoji} **{war[12]}**"
        
        embed = create_embed(title, description, discord.Color.orange())
        
        # War info
        embed.add_field(
            name="📊 Savaş Bilgileri",
            value=f"**Durum:** {war[3].title()}\n"
                  f"**Başlangıç:** <t:{int(datetime.fromisoformat(war[6].replace('Z', '+00:00')).timestamp())}:R>\n"
                  f"{weather_emoji} **Hava:** {war[8].title()}\n"
                  f"{terrain_emoji} **Arazi:** {war[9].title()}",
            inline=True
        )
        
        # Casualties
        embed.add_field(
            name="💀 Kayıplar",
            value=f"{att_emoji} {format_number(war[4])} asker\n"
                  f"{def_emoji} {format_number(war[5])} asker",
            inline=True
        )
        
        # Recent battles
        if battles:
            battle_history = []
            for battle in battles[:5]:  # Show last 5 battles
                turn_num, att_action, def_action, result, _, _, timestamp = battle
                battle_history.append(f"**Tur {turn_num}:** {att_action} vs {def_action}")
            
            embed.add_field(
                name="📜 Son Turlar",
                value="\n".join(battle_history),
                inline=False
            )
        
        return embed

    def get_available_actions(self):
        """Get list of available battle actions"""
        return list(self.battle_actions.keys())

    def get_action_description(self, action):
        """Get description for a battle action"""
        action_info = self.battle_actions.get(action)
        if action_info:
            return f"{action_info['description']} (Saldırı: {action_info['damage_multiplier']:.1f}x, Savunma: {action_info['defense_multiplier']:.1f}x)"
        return "Bilinmeyen aksiyon"
