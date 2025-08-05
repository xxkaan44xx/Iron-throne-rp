import asyncio
import logging
from datetime import datetime, timedelta
from utils import format_number

logger = logging.getLogger(__name__)

class EconomySystem:
    def __init__(self, database):
        self.db = database

    async def generate_income(self):
        """Generate income from all income sources"""
        try:
            # Get all active income sources that haven't generated income in the last minute
            self.db.c.execute('''
            SELECT income_sources.*, a.name as house_name
            FROM income_sources
            LEFT JOIN alliances a ON (income_sources.house_id = a.id)
            LEFT JOIN alliances a2 ON (income_sources.seized_by = a2.id)
            WHERE datetime(income_sources.last_income) <= datetime('now', '-1 minute')
            AND (a.id IS NOT NULL OR a2.id IS NOT NULL)
            ''')
            
            sources = self.db.c.fetchall()
            
            income_generated = 0
            for source in sources:
                source_id = source[0]
                house_id = source[1]
                seized_by = source[10]
                income_per_minute = source[5]
                
                # Determine who gets the income (owner or seizer)
                beneficiary_id = seized_by if source[9] else house_id  # seized field check
                
                if beneficiary_id:
                    # Add income to alliance
                    success = self.db.update_alliance_resources(beneficiary_id, income_per_minute, 0)
                    
                    if success:
                        # Update last income timestamp
                        self.db.c.execute('''
                        UPDATE income_sources 
                        SET last_income = CURRENT_TIMESTAMP 
                        WHERE id = ?
                        ''', (source_id,))
                        income_generated += income_per_minute
            
            self.db.conn.commit()
            
            if income_generated > 0:
                logger.info(f"Generated {income_generated} gold from {len(sources)} income sources")
            
        except Exception as e:
            logger.error(f"Income generation error: {e}")

    async def calculate_debt_interest(self):
        """Calculate and apply interest to all active debts"""
        try:
            # Get all active debts
            self.db.c.execute('''
            SELECT id, debtor_house_id, amount, interest_rate, creditor_house_id
            FROM house_debts 
            WHERE status = 'active' AND amount > 0
            ''')
            
            debts = self.db.c.fetchall()
            
            total_interest = 0
            for debt in debts:
                debt_id, debtor_id, amount, interest_rate, creditor_id = debt
                
                # Calculate hourly interest (annual rate / 8760 hours)
                hourly_rate = interest_rate / 8760
                interest = max(1, int(amount * hourly_rate))  # Minimum 1 gold interest
                new_amount = amount + interest
                
                # Update debt amount
                self.db.c.execute('''
                UPDATE house_debts 
                SET amount = ?
                WHERE id = ?
                ''', (new_amount, debt_id))
                
                # Add interest to house debt total
                self.db.c.execute('''
                UPDATE alliances 
                SET debt = debt + ?
                WHERE id = ?
                ''', (interest, debtor_id))
                
                total_interest += interest
            
            self.db.conn.commit()
            
            if total_interest > 0:
                logger.info(f"Applied {total_interest} gold in debt interest to {len(debts)} debts")
            
        except Exception as e:
            logger.error(f"Debt calculation error: {e}")

    def create_loan(self, creditor_id, debtor_id, amount, interest_rate=0.1, duration_days=30):
        """Create a loan between houses"""
        try:
            # Input validation
            if amount <= 0:
                return False, "Borç miktarı pozitif olmalı!"
            
            if interest_rate < 0 or interest_rate > 1:
                return False, "Faiz oranı 0-100% arasında olmalı!"
            
            if duration_days < 1 or duration_days > 365:
                return False, "Borç süresi 1-365 gün aralığında olmalı!"
            
            # Check if creditor has enough gold
            creditor = self.db.get_alliance_by_id(creditor_id)
            if not creditor or creditor[3] < amount:  # gold field
                return False, "Yetersiz altın! Borç verecek kadar altınınız yok."
            
            # Check if debtor exists
            debtor = self.db.get_alliance_by_id(debtor_id)
            if not debtor:
                return False, "Hedef hane bulunamadı!"
            
            # Check if same house
            if creditor_id == debtor_id:
                return False, "Kendinize borç veremezsiniz!"
            
            # Calculate due date
            due_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
            
            # Transfer gold
            if not self.db.update_alliance_resources(creditor_id, -amount, 0):
                return False, "Altın transferi başarısız!"
            
            if not self.db.update_alliance_resources(debtor_id, amount, 0):
                # Rollback creditor transaction
                self.db.update_alliance_resources(creditor_id, amount, 0)
                return False, "Altın transferi başarısız!"
            
            # Create debt record
            self.db.c.execute('''
            INSERT INTO house_debts (debtor_house_id, creditor_house_id, amount, due_date, interest_rate)
            VALUES (?, ?, ?, ?, ?)
            ''', (debtor_id, creditor_id, amount, due_date, interest_rate))
            
            # Update debtor's total debt
            self.db.c.execute('''
            UPDATE alliances 
            SET debt = debt + ?
            WHERE id = ?
            ''', (amount, debtor_id))
            
            self.db.conn.commit()
            
            return True, f"{format_number(amount)} altın başarıyla borç olarak verildi! Vade: {duration_days} gün, Faiz: %{int(interest_rate*100)}"
            
        except Exception as e:
            logger.error(f"Loan creation error: {e}")
            return False, f"Borç verme hatası: {str(e)}"

    def repay_debt(self, debtor_id, amount):
        """Repay debt for a house"""
        try:
            if amount <= 0:
                return False, "Ödeme miktarı pozitif olmalı!"
            
            # Get house data
            debtor = self.db.get_alliance_by_id(debtor_id)
            if not debtor or debtor[3] < amount:  # gold field
                return False, f"Yetersiz altın! Gerekli: {format_number(amount)}, Mevcut: {format_number(debtor[3] if debtor else 0)}"
            
            # Get oldest debt
            self.db.c.execute('''
            SELECT id, creditor_house_id, amount
            FROM house_debts 
            WHERE debtor_house_id = ? AND status = 'active' AND amount > 0
            ORDER BY created_at ASC
            LIMIT 1
            ''', (debtor_id,))
            
            debt = self.db.c.fetchone()
            if not debt:
                return False, "Ödenmemiş borç bulunamadı!"
            
            debt_id, creditor_id, debt_amount = debt
            payment = min(amount, debt_amount)
            
            # Transfer gold
            if not self.db.update_alliance_resources(debtor_id, -payment, 0):
                return False, "Ödeme transferi başarısız!"
            
            if not self.db.update_alliance_resources(creditor_id, payment, 0):
                # Rollback debtor transaction
                self.db.update_alliance_resources(debtor_id, payment, 0)
                return False, "Ödeme transferi başarısız!"
            
            # Update debt
            remaining_debt = debt_amount - payment
            if remaining_debt <= 0:
                # Debt fully paid
                self.db.c.execute('''
                UPDATE house_debts 
                SET status = 'paid', amount = 0
                WHERE id = ?
                ''', (debt_id,))
            else:
                # Partial payment
                self.db.c.execute('''
                UPDATE house_debts 
                SET amount = ?
                WHERE id = ?
                ''', (remaining_debt, debt_id))
            
            # Update house total debt
            self.db.c.execute('''
            UPDATE alliances 
            SET debt = debt - ?
            WHERE id = ?
            ''', (payment, debtor_id))
            
            self.db.conn.commit()
            
            if remaining_debt <= 0:
                return True, f"{format_number(payment)} Lannister Altını ödendi! Borç tamamen kapatıldı. 🎉"
            else:
                return True, f"{format_number(payment)} Lannister Altını ödendi! Kalan borç: {format_number(remaining_debt)} Lannister Altını"
            
        except Exception as e:
            logger.error(f"Debt repayment error: {e}")
            return False, f"Borç ödeme hatası: {str(e)}"

    def get_house_economy_status(self, house_id):
        """Get detailed economic status for a house"""
        try:
            house = self.db.get_alliance_by_id(house_id)
            if not house:
                return None
            
            # Get income sources (owned and seized)
            owned_sources = []
            seized_sources = []
            
            all_sources = self.db.get_income_sources(house_id)
            for source in all_sources:
                if source[9]:  # seized field
                    if source[10] == house_id:  # seized_by field
                        seized_sources.append(source)
                else:
                    if source[1] == house_id:  # house_id field
                        owned_sources.append(source)
            
            # Calculate total income
            owned_income = sum(source[5] for source in owned_sources)  # income_per_minute
            seized_income = sum(source[5] for source in seized_sources)
            total_income = owned_income + seized_income
            
            # Get debts owed by this house
            self.db.c.execute('''
            SELECT hd.*, a.name as creditor_name
            FROM house_debts hd
            JOIN alliances a ON hd.creditor_house_id = a.id
            WHERE hd.debtor_house_id = ? AND hd.status = 'active' AND hd.amount > 0
            ORDER BY hd.due_date ASC
            ''', (house_id,))
            debts_owed = self.db.c.fetchall()
            
            # Get debts owed to this house
            self.db.c.execute('''
            SELECT hd.*, a.name as debtor_name
            FROM house_debts hd
            JOIN alliances a ON hd.debtor_house_id = a.id
            WHERE hd.creditor_house_id = ? AND hd.status = 'active' AND hd.amount > 0
            ORDER BY hd.due_date ASC
            ''', (house_id,))
            debts_receivable = self.db.c.fetchall()
            
            return {
                "house": house,
                "total_income_per_minute": total_income,
                "owned_income": owned_income,
                "seized_income": seized_income,
                "owned_sources": owned_sources,
                "seized_sources": seized_sources,
                "debts_owed": debts_owed,
                "debts_receivable": debts_receivable,
                "total_debt_owed": sum(debt[3] for debt in debts_owed),  # amount field
                "total_debt_receivable": sum(debt[3] for debt in debts_receivable)
            }
            
        except Exception as e:
            logger.error(f"Error getting house economy status: {e}")
            return None

    def calculate_house_net_worth(self, house_id):
        """Calculate total net worth of a house"""
        try:
            economy_status = self.get_house_economy_status(house_id)
            if not economy_status:
                return 0
            
            house = economy_status["house"]
            gold = house[3] or 0
            soldiers_value = (house[4] or 0) * 10  # Each soldier worth 10 gold
            
            # Value of income sources (owned only)
            sources_value = sum(source[6] for source in economy_status["owned_sources"])  # cost field
            
            # Subtract debts owed
            total_debts_owed = economy_status["total_debt_owed"]
            
            # Add receivable debts (partial value, as they might not be collected)
            receivable_value = economy_status["total_debt_receivable"] * 0.8  # 80% collection rate assumption
            
            net_worth = gold + soldiers_value + sources_value - total_debts_owed + receivable_value
            return max(0, int(net_worth))
            
        except Exception as e:
            logger.error(f"Error calculating net worth: {e}")
            return 0

    def create_income_source(self, house_id, source_type, name, region, base_income=100, cost_multiplier=1.0):
        """Create a new income source for a house"""
        try:
            # Validate inputs
            if not name or len(name.strip()) < 3:
                return False, "Gelir kaynağı adı en az 3 karakter olmalı!"
            
            if not region or len(region.strip()) < 2:
                return False, "Bölge adı en az 2 karakter olmalı!"
            
            # Calculate cost and income based on source type
            base_costs = {
                "mine": 2000,
                "farm": 1000, 
                "port": 1500,
                "castle": 3000,
                "market": 1200,
                "forest": 800,
                "quarry": 1100,
                "vineyard": 900
            }
            
            base_incomes = {
                "mine": 150,
                "farm": 80,
                "port": 120,
                "castle": 200,
                "market": 100,
                "forest": 60,
                "quarry": 90,
                "vineyard": 70
            }
            
            cost = int(base_costs.get(source_type, 1000) * cost_multiplier)
            income_per_minute = int(base_incomes.get(source_type, base_income))
            
            # Check if house has enough gold
            house = self.db.get_alliance_by_id(house_id)
            if not house or house[3] < cost:
                return False, f"Yetersiz altın! Gerekli: {format_number(cost)}, Mevcut: {format_number(house[3] if house else 0)}"
            
            # Deduct cost
            if not self.db.update_alliance_resources(house_id, -cost, 0):
                return False, "Altın düşülemedi!"
            
            # Create income source
            source_id = self.db.add_income_source(house_id, source_type, name.strip(), region.strip(), income_per_minute, cost)
            
            if source_id:
                return True, f"'{name}' gelir kaynağı oluşturuldu! Dakikalık gelir: {format_number(income_per_minute)} altın"
            else:
                # Rollback payment
                self.db.update_alliance_resources(house_id, cost, 0)
                return False, "Gelir kaynağı oluşturulamadı!"
            
        except Exception as e:
            logger.error(f"Error creating income source: {e}")
            return False, f"Gelir kaynağı oluşturma hatası: {str(e)}"

    def get_income_source_types(self):
        """Get available income source types"""
        return {
            "mine": {"name": "Maden", "base_income": 150, "base_cost": 2000, "emoji": "⛏️"},
            "farm": {"name": "Çiftlik", "base_income": 80, "base_cost": 1000, "emoji": "🌾"},
            "port": {"name": "Liman", "base_income": 120, "base_cost": 1500, "emoji": "⚓"},
            "castle": {"name": "Kale", "base_income": 200, "base_cost": 3000, "emoji": "🏰"},
            "market": {"name": "Pazar", "base_income": 100, "base_cost": 1200, "emoji": "🏪"},
            "forest": {"name": "Orman", "base_income": 60, "base_cost": 800, "emoji": "🌲"},
            "quarry": {"name": "Taş Ocağı", "base_income": 90, "base_cost": 1100, "emoji": "🪨"},
            "vineyard": {"name": "Bağ", "base_income": 70, "base_cost": 900, "emoji": "🍇"}
        }

    def buy_soldiers(self, house_id, soldier_count):
        """Buy soldiers for a house"""
        try:
            if soldier_count <= 0:
                return False, "Asker sayısı pozitif olmalı!"
            
            # Calculate cost (10 gold per soldier)
            cost_per_soldier = 10
            total_cost = soldier_count * cost_per_soldier
            
            # Check if house has enough gold
            house = self.db.get_alliance_by_id(house_id)
            if not house or house[3] < total_cost:
                return False, f"Yetersiz altın! Gerekli: {format_number(total_cost)}, Mevcut: {format_number(house[3] if house else 0)}"
            
            # Purchase soldiers
            success = self.db.update_alliance_resources(house_id, -total_cost, soldier_count)
            
            if success:
                return True, f"{format_number(soldier_count)} asker satın alındı! Toplam maliyet: {format_number(total_cost)} altın"
            else:
                return False, "Asker satın alma işlemi başarısız!"
            
        except Exception as e:
            logger.error(f"Error buying soldiers: {e}")
            return False, f"Asker satın alma hatası: {str(e)}"
