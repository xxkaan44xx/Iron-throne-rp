
import logging
import discord
import random
import asyncio
from datetime import datetime, timedelta
from utils import create_embed, format_number, get_house_emoji, get_character_class_info

logger = logging.getLogger(__name__)

class TournamentSystem:
    def __init__(self, database):
        self.db = database
        
        # Tournament types and their characteristics
        self.tournament_types = {
            'joust': {
                'name': 'Mızrak Turnuvası',
                'emoji': '🏇',
                'skill_factor': 'cavalry_skill',
                'equipment_bonus': 'lance_quality',
                'description': 'Atla mızrak dövüşü'
            },
            'melee': {
                'name': 'Kılıç Turnuvası', 
                'emoji': '⚔️',
                'skill_factor': 'sword_skill',
                'equipment_bonus': 'sword_quality',
                'description': 'Çok kişili kılıç dövüşü'
            },
            'archery': {
                'name': 'Okçuluk Turnuvası',
                'emoji': '🏹',
                'skill_factor': 'archery_skill',
                'equipment_bonus': 'bow_quality',
                'description': 'Uzaktan nişan yarışması'
            },
            'mixed': {
                'name': 'Karma Turnuva',
                'emoji': '🏆',
                'skill_factor': 'overall_skill',
                'equipment_bonus': 'equipment_quality',
                'description': 'Tüm yeteneklerin karışımı'
            }
        }
        
        # Duel types
        self.duel_types = {
            'sword': {
                'name': 'Kılıç Düellosu',
                'emoji': '⚔️',
                'description': 'Geleneksel kılıç dövüşü'
            },
            'lance': {
                'name': 'Mızrak Düellosu', 
                'emoji': '🏇',
                'description': 'Atlı mızrak dövüşü'
            },
            'trial_by_combat': {
                'name': 'Savaş Mahkemesi',
                'emoji': '⚖️',
                'description': 'Ölümüne dövüş'
            }
        }

    def create_tournament(self, host_house_id, tournament_name, tournament_type, entry_fee=1000, prize_pool=10000, max_participants=16):
        """Create a new tournament"""
        try:
            if tournament_type not in self.tournament_types:
                return False, f"Geçersiz turnuva türü! Kullanılabilir: {', '.join(self.tournament_types.keys())}"
            
            # Check if host house exists and has enough gold for prize
            host_house = self.db.get_alliance_by_id(host_house_id)
            if not host_house:
                return False, "Ev sahibi hane bulunamadı!"
            
            if host_house[3] < prize_pool:
                return False, f"Yetersiz altın! Turnuva ödülü için {format_number(prize_pool)} altın gerekli."
            
            # Deduct prize pool from host house
            self.db.update_alliance_resources(host_house_id, -prize_pool, 0)
            
            # Create tournament
            self.db.c.execute('''
            INSERT INTO tournaments (name, host_house_id, tournament_type, entry_fee, prize_pool, max_participants)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (tournament_name, host_house_id, tournament_type, entry_fee, prize_pool, max_participants))
            
            tournament_id = self.db.c.lastrowid
            self.db.conn.commit()
            
            return True, f"🏆 **{tournament_name}** turnuvası oluşturuldu! ID: {tournament_id}"
            
        except Exception as e:
            logger.error(f"Error creating tournament: {e}")
            return False, f"Turnuva oluşturma hatası: {str(e)}"

    def join_tournament(self, tournament_id, user_id):
        """Join a tournament"""
        try:
            # Check if tournament exists and is open
            self.db.c.execute('SELECT * FROM tournaments WHERE id = ? AND status = "open"', (tournament_id,))
            tournament = self.db.c.fetchone()
            if not tournament:
                return False, "Turnuva bulunamadı veya kayıtlar kapandı!"
            
            # Check if user is in an alliance
            user_alliance = self.db.get_user_alliance(user_id)
            if not user_alliance:
                return False, "Turnuvaya katılmak için bir haneye üye olmalısın!"
            
            # Check if already joined
            self.db.c.execute('SELECT id FROM tournament_participants WHERE tournament_id = ? AND user_id = ?', 
                            (tournament_id, user_id))
            if self.db.c.fetchone():
                return False, "Bu turnuvaya zaten katıldın!"
            
            # Check participant limit
            self.db.c.execute('SELECT COUNT(*) FROM tournament_participants WHERE tournament_id = ?', (tournament_id,))
            current_participants = self.db.c.fetchone()[0]
            if current_participants >= tournament[10]:  # max_participants
                return False, "Turnuva dolu!"
            
            # Check entry fee
            alliance = self.db.get_alliance_by_id(user_alliance[0])
            entry_fee = tournament[5]
            if alliance[3] < entry_fee:
                return False, f"Yetersiz altın! Katılım ücreti: {format_number(entry_fee)} altın"
            
            # Calculate character skill based on tournament type
            character_skill = self._calculate_tournament_skill(user_id, tournament[3])  # tournament_type
            
            # Deduct entry fee and join tournament
            self.db.update_alliance_resources(user_alliance[0], -entry_fee, 0)
            
            self.db.c.execute('''
            INSERT INTO tournament_participants (tournament_id, user_id, character_skill)
            VALUES (?, ?, ?)
            ''', (tournament_id, user_id, character_skill))
            
            self.db.conn.commit()
            
            return True, f"Turnuvaya başarıyla katıldın! Yetenek puanın: {character_skill}"
            
        except Exception as e:
            logger.error(f"Error joining tournament: {e}")
            return False, f"Turnuvaya katılma hatası: {str(e)}"

    def start_tournament(self, tournament_id):
        """Start and simulate tournament"""
        try:
            # Get tournament and participants
            self.db.c.execute('SELECT * FROM tournaments WHERE id = ? AND status = "open"', (tournament_id,))
            tournament = self.db.c.fetchone()
            if not tournament:
                return False, "Turnuva bulunamadı!"
            
            self.db.c.execute('SELECT * FROM tournament_participants WHERE tournament_id = ?', (tournament_id,))
            participants = self.db.c.fetchall()
            
            if len(participants) < 2:
                return False, "En az 2 katılımcı gerekli!"
            
            # Start tournament
            self.db.c.execute('UPDATE tournaments SET status = "active", start_time = CURRENT_TIMESTAMP WHERE id = ?', 
                            (tournament_id,))
            
            # Simulate tournament brackets
            results = self._simulate_tournament_brackets(participants, tournament[3])  # tournament_type
            
            # Distribute prizes
            prize_pool = tournament[6]  # prize_pool
            self._distribute_tournament_prizes(tournament_id, results, prize_pool)
            
            # End tournament
            self.db.c.execute('UPDATE tournaments SET status = "completed", end_time = CURRENT_TIMESTAMP WHERE id = ?', 
                            (tournament_id,))
            self.db.conn.commit()
            
            return True, results
            
        except Exception as e:
            logger.error(f"Error starting tournament: {e}")
            return False, f"Turnuva başlatma hatası: {str(e)}"

    def challenge_to_duel(self, challenger_id, challenged_id, duel_type, wager=0):
        """Challenge someone to a duel"""
        try:
            if challenger_id == challenged_id:
                return False, "Kendine düello teklif edemezsin!"
            
            if duel_type not in self.duel_types:
                return False, f"Geçersiz düello türü! Kullanılabilir: {', '.join(self.duel_types.keys())}"
            
            # Check if both users are in alliances
            challenger_alliance = self.db.get_user_alliance(challenger_id)
            challenged_alliance = self.db.get_user_alliance(challenged_id)
            
            if not challenger_alliance or not challenged_alliance:
                return False, "Her iki taraf da bir haneye üye olmalı!"
            
            # Check for existing active duel
            self.db.c.execute('''
            SELECT id FROM duels WHERE 
            ((challenger_id = ? AND challenged_id = ?) OR (challenger_id = ? AND challenged_id = ?))
            AND status = "challenged"
            ''', (challenger_id, challenged_id, challenged_id, challenger_id))
            
            if self.db.c.fetchone():
                return False, "Bu kişiyle zaten aktif bir düello var!"
            
            # Check wager
            if wager > 0:
                challenger_house = self.db.get_alliance_by_id(challenger_alliance[0])
                if challenger_house[3] < wager:
                    return False, f"Yetersiz altın! Bahis: {format_number(wager)} altın"
            
            # Create duel challenge
            self.db.c.execute('''
            INSERT INTO duels (challenger_id, challenged_id, duel_type, wager_amount)
            VALUES (?, ?, ?, ?)
            ''', (challenger_id, challenged_id, duel_type, wager))
            
            duel_id = self.db.c.lastrowid
            self.db.conn.commit()
            
            return True, f"Düello teklifi gönderildi! ID: {duel_id}"
            
        except Exception as e:
            logger.error(f"Error challenging to duel: {e}")
            return False, f"Düello teklifi hatası: {str(e)}"

    def accept_duel(self, duel_id, challenged_id):
        """Accept a duel challenge"""
        try:
            # Get duel
            self.db.c.execute('SELECT * FROM duels WHERE id = ? AND challenged_id = ? AND status = "challenged"', 
                            (duel_id, challenged_id))
            duel = self.db.c.fetchone()
            if not duel:
                return False, "Düello bulunamadı veya kabul edilemez!"
            
            # Check wager
            wager = duel[4]  # wager_amount
            if wager > 0:
                challenged_alliance = self.db.get_user_alliance(challenged_id)
                challenged_house = self.db.get_alliance_by_id(challenged_alliance[0])
                if challenged_house[3] < wager:
                    return False, f"Yetersiz altın! Bahis: {format_number(wager)} altın"
            
            # Simulate duel
            result = self._simulate_duel(duel[1], duel[2], duel[3])  # challenger_id, challenged_id, duel_type
            winner_id = result['winner_id']
            
            # Update duel
            self.db.c.execute('''
            UPDATE duels SET status = "completed", winner_id = ?, fight_details = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (winner_id, result['details'], duel_id))
            
            # Handle wager
            if wager > 0:
                challenger_alliance = self.db.get_user_alliance(duel[1])
                challenged_alliance = self.db.get_user_alliance(duel[2])
                
                # Deduct wager from both
                self.db.update_alliance_resources(challenger_alliance[0], -wager, 0)
                self.db.update_alliance_resources(challenged_alliance[0], -wager, 0)
                
                # Give double to winner
                winner_alliance = self.db.get_user_alliance(winner_id)
                self.db.update_alliance_resources(winner_alliance[0], wager * 2, 0)
            
            self.db.conn.commit()
            
            return True, result
            
        except Exception as e:
            logger.error(f"Error accepting duel: {e}")
            return False, f"Düello kabul etme hatası: {str(e)}"

    def _calculate_tournament_skill(self, user_id, tournament_type):
        """Calculate character skill for tournament"""
        # Get character data
        character = self.db.get_user_member_data(user_id)
        if not character:
            return 50
        
        # Base skill from character class and level
        class_info = get_character_class_info(character[4] or "Lord")
        base_skill = 40 + (character[6] or 0) // 100  # experience based
        
        # Add class bonuses
        base_skill += class_info['bonuses']['attack']
        
        # Tournament type specific bonuses
        if tournament_type == 'joust' and character[4] == 'Knight':
            base_skill += 15
        elif tournament_type == 'archery' and character[4] == 'Assassin':
            base_skill += 20
        elif tournament_type == 'melee' and character[4] in ['Knight', 'Sellsword']:
            base_skill += 10
        
        return min(100, max(20, base_skill + random.randint(-10, 10)))

    def _simulate_tournament_brackets(self, participants, tournament_type):
        """Simulate tournament elimination brackets"""
        results = []
        current_round = list(participants)
        round_num = 1
        
        while len(current_round) > 1:
            next_round = []
            round_matches = []
            
            # Pair participants
            random.shuffle(current_round)
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    p1, p2 = current_round[i], current_round[i + 1]
                    
                    # Simulate match
                    winner = self._simulate_tournament_match(p1, p2, tournament_type)
                    loser = p2 if winner == p1 else p1
                    
                    # Update eliminated status
                    self.db.c.execute('UPDATE tournament_participants SET eliminated = 1 WHERE id = ?', 
                                    (loser[0],))
                    
                    next_round.append(winner)
                    round_matches.append({
                        'winner': winner,
                        'loser': loser,
                        'round': round_num
                    })
                else:
                    # Bye to next round
                    next_round.append(current_round[i])
            
            results.extend(round_matches)
            current_round = next_round
            round_num += 1
        
        # Set final positions
        if current_round:
            champion = current_round[0]
            self.db.c.execute('UPDATE tournament_participants SET final_position = 1 WHERE id = ?', 
                            (champion[0],))
        
        return results

    def _simulate_tournament_match(self, p1, p2, tournament_type):
        """Simulate a single tournament match"""
        skill1 = p1[3] + p1[4]  # character_skill + equipment_bonus
        skill2 = p2[3] + p2[4]
        
        # Add randomness
        roll1 = skill1 + random.randint(1, 30)
        roll2 = skill2 + random.randint(1, 30)
        
        return p1 if roll1 > roll2 else p2

    def _simulate_duel(self, challenger_id, challenged_id, duel_type):
        """Simulate a duel between two characters"""
        # Get character data
        challenger_data = self.db.get_user_member_data(challenger_id)
        challenged_data = self.db.get_user_member_data(challenged_id)
        
        # Calculate combat scores
        challenger_score = self._calculate_duel_score(challenger_data, duel_type)
        challenged_score = self._calculate_duel_score(challenged_data, duel_type)
        
        # Add randomness for excitement
        challenger_roll = challenger_score + random.randint(1, 50)
        challenged_roll = challenged_score + random.randint(1, 50)
        
        winner_id = challenger_id if challenger_roll > challenged_roll else challenged_id
        
        # Generate fight details
        details = self._generate_fight_details(duel_type, challenger_roll, challenged_roll)
        
        return {
            'winner_id': winner_id,
            'challenger_score': challenger_roll,
            'challenged_score': challenged_roll,
            'details': details
        }

    def _calculate_duel_score(self, character_data, duel_type):
        """Calculate duel combat score"""
        if not character_data:
            return 50
        
        base_score = (character_data[8] or 20) + (character_data[9] or 15)  # attack + defense
        
        # Class bonuses
        class_info = get_character_class_info(character_data[4] or "Lord")
        base_score += sum(class_info['bonuses'].values())
        
        # Duel type bonuses
        if duel_type == 'sword' and character_data[4] in ['Knight', 'Sellsword']:
            base_score += 15
        elif duel_type == 'lance' and character_data[4] == 'Knight':
            base_score += 20
        elif duel_type == 'trial_by_combat':
            base_score += 10  # High stakes bonus
        
        return base_score

    def _generate_fight_details(self, duel_type, score1, score2):
        """Generate descriptive fight details"""
        margin = abs(score1 - score2)
        
        if margin > 30:
            outcome = "ezici zafer"
        elif margin > 15:
            outcome = "net zafer"
        else:
            outcome = "çekişmeli dövüş"
        
        duel_desc = self.duel_types[duel_type]['description']
        
        return f"{duel_desc} - {outcome} ({score1} vs {score2})"

    def _distribute_tournament_prizes(self, tournament_id, results, total_prize):
        """Distribute tournament prize money"""
        try:
            # Prize distribution: 50% champion, 30% runner-up, 20% semi-finalists
            champion_prize = int(total_prize * 0.5)
            runner_up_prize = int(total_prize * 0.3)
            semi_finalist_prize = int(total_prize * 0.1)
            
            # Find champion (last winner)
            if results:
                final_match = results[-1]
                champion = final_match['winner']
                
                # Award champion
                self.db.c.execute('UPDATE tournament_participants SET prize_won = ? WHERE id = ?', 
                                (champion_prize, champion[0]))
                
                champion_alliance = self.db.get_user_alliance(champion[1])  # user_id
                if champion_alliance:
                    self.db.update_alliance_resources(champion_alliance[0], champion_prize, 0)
            
        except Exception as e:
            logger.error(f"Error distributing prizes: {e}")

    def create_tournament_embed(self, tournament_data, participants=None):
        """Create Discord embed for tournament display"""
        if not tournament_data:
            return create_embed("❌ Hata", "Turnuva bilgileri alınamadı!", discord.Color.red())
        
        tournament_type_info = self.tournament_types[tournament_data[3]]
        
        embed = create_embed(
            f"{tournament_type_info['emoji']} {tournament_data[1]}",
            f"{tournament_type_info['description']}",
            discord.Color.gold()
        )
        
        embed.add_field(name="💰 Katılım Ücreti", value=f"{format_number(tournament_data[5])} altın", inline=True)
        embed.add_field(name="🏆 Ödül Havuzu", value=f"{format_number(tournament_data[6])} altın", inline=True)
        embed.add_field(name="👥 Maksimum Katılımcı", value=str(tournament_data[10]), inline=True)
        
        if participants:
            participant_count = len(participants)
            embed.add_field(name="📊 Durum", 
                          value=f"{participant_count}/{tournament_data[10]} katılımcı\n"
                                f"Durum: {tournament_data[7].title()}", 
                          inline=False)
        
        embed.set_footer(text=f"Turnuva ID: {tournament_data[0]} | !turnuva_katıl {tournament_data[0]} ile katıl")
        
        return embed
