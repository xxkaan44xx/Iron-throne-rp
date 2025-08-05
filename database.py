import sqlite3
import json
import logging
from datetime import datetime, timedelta
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=DATABASE_PATH):
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.c = self.conn.cursor()
            self.create_tables()
            self.populate_default_data()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def create_tables(self):
        """Create all necessary database tables"""

        # Alliances/Houses table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS alliances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            leader_id INTEGER,
            gold INTEGER DEFAULT 1000,
            soldiers INTEGER DEFAULT 100,
            power_points INTEGER DEFAULT 0,
            house_type TEXT DEFAULT 'Custom',
            special_ability TEXT DEFAULT '',
            region TEXT DEFAULT '',
            debt INTEGER DEFAULT 0,
            army_quality INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Handle schema migrations - add army_quality column if it doesn't exist
        try:
            self.c.execute('SELECT army_quality FROM alliances LIMIT 1')
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            self.c.execute('ALTER TABLE alliances ADD COLUMN army_quality INTEGER DEFAULT 50')
            logger.info("Added army_quality column to alliances table")

        # Members table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            user_id INTEGER PRIMARY KEY,
            alliance_id INTEGER,
            role TEXT DEFAULT 'Üye',
            married_to INTEGER,
            character_class TEXT DEFAULT 'Lord',
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            health INTEGER DEFAULT 100,
            attack_power INTEGER DEFAULT 20,
            defense INTEGER DEFAULT 15,
            special_skills TEXT DEFAULT '[]',
            legendary_weapon TEXT DEFAULT '',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(alliance_id) REFERENCES alliances(id),
            FOREIGN KEY(married_to) REFERENCES members(user_id)
        )
        ''')

        # Wars table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS wars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attacker_id INTEGER NOT NULL,
            defender_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            attacker_losses INTEGER DEFAULT 0,
            defender_losses INTEGER DEFAULT 0,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            weather TEXT DEFAULT 'normal',
            terrain TEXT DEFAULT 'ova',
            winner_id INTEGER,
            FOREIGN KEY(attacker_id) REFERENCES alliances(id),
            FOREIGN KEY(defender_id) REFERENCES alliances(id),
            FOREIGN KEY(winner_id) REFERENCES alliances(id)
        )
        ''')

        # Battle logs table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS battle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            war_id INTEGER NOT NULL,
            turn_number INTEGER NOT NULL,
            attacker_action TEXT NOT NULL,
            defender_action TEXT NOT NULL,
            result TEXT NOT NULL,
            attacker_damage INTEGER DEFAULT 0,
            defender_damage INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(war_id) REFERENCES wars(id)
        )
        ''')

        # ASOIAF Characters table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS asoiaf_characters (
            user_id INTEGER PRIMARY KEY,
            character_name TEXT UNIQUE NOT NULL,
            house TEXT NOT NULL,
            title TEXT NOT NULL,
            alive BOOLEAN DEFAULT 1,
            age INTEGER DEFAULT 25,
            skills TEXT DEFAULT '[]',
            relationships TEXT DEFAULT '{}',
            backstory TEXT DEFAULT '',
            FOREIGN KEY(user_id) REFERENCES members(user_id)
        )
        ''')

        # House debts table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS house_debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debtor_house_id INTEGER NOT NULL,
            creditor_house_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            interest_rate REAL DEFAULT 0.1,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(debtor_house_id) REFERENCES alliances(id),
            FOREIGN KEY(creditor_house_id) REFERENCES alliances(id)
        )
        ''')

        # Income sources table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS income_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_id INTEGER NOT NULL,
            source_type TEXT NOT NULL,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            income_per_minute INTEGER NOT NULL,
            cost INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            seized BOOLEAN DEFAULT 0,
            seized_by INTEGER,
            last_income TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(house_id) REFERENCES alliances(id),
            FOREIGN KEY(seized_by) REFERENCES alliances(id)
        )
        ''')

        # Marriages table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS marriages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            married_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'married',
            FOREIGN KEY(user1_id) REFERENCES members(user_id),
            FOREIGN KEY(user2_id) REFERENCES members(user_id),
            UNIQUE(user1_id, user2_id)
        )
        ''')

        # Pregnancies table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS pregnancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mother_id INTEGER NOT NULL,
            father_id INTEGER NOT NULL,
            conception_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pregnant',
            baby_name TEXT,
            baby_gender TEXT,
            FOREIGN KEY(mother_id) REFERENCES members(user_id),
            FOREIGN KEY(father_id) REFERENCES members(user_id)
        )
        ''')

        # Children table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            birth_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mother_id INTEGER NOT NULL,
            father_id INTEGER NOT NULL,
            house_id INTEGER NOT NULL,
            age_years INTEGER DEFAULT 0,
            traits TEXT DEFAULT '[]',
            FOREIGN KEY(mother_id) REFERENCES members(user_id),
            FOREIGN KEY(father_id) REFERENCES members(user_id),
            FOREIGN KEY(house_id) REFERENCES alliances(id)
        )
        ''')

        # Heirs table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS heirs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_id INTEGER NOT NULL,
            heir_user_id INTEGER NOT NULL,
            succession_order INTEGER DEFAULT 1,
            appointed_by INTEGER NOT NULL,
            appointed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(house_id) REFERENCES alliances(id),
            FOREIGN KEY(heir_user_id) REFERENCES members(user_id),
            FOREIGN KEY(appointed_by) REFERENCES members(user_id)
        )
        ''')

        # Army resources table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS army_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_id INTEGER NOT NULL,
            food_supplies INTEGER DEFAULT 1000,
            weapons_quality INTEGER DEFAULT 50,
            armor_quality INTEGER DEFAULT 50,
            siege_weapons INTEGER DEFAULT 0,
            cavalry INTEGER DEFAULT 0,
            archers INTEGER DEFAULT 0,
            infantry INTEGER DEFAULT 0,
            navy_ships INTEGER DEFAULT 0,
            army_training INTEGER DEFAULT 50,
            morale INTEGER DEFAULT 70,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(house_id) REFERENCES alliances(id)
        )
        ''')

        # Tournaments table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host_house_id INTEGER NOT NULL,
            tournament_type TEXT CHECK(tournament_type IN ('joust', 'melee', 'archery', 'mixed')),
            entry_fee INTEGER DEFAULT 1000,
            prize_pool INTEGER DEFAULT 10000,
            status TEXT DEFAULT 'open',
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            max_participants INTEGER DEFAULT 16,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(host_house_id) REFERENCES alliances(id)
        )
        ''')

        # Tournament participants table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS tournament_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            character_skill INTEGER DEFAULT 50,
            equipment_bonus INTEGER DEFAULT 0,
            eliminated BOOLEAN DEFAULT 0,
            final_position INTEGER,
            prize_won INTEGER DEFAULT 0,
            FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
            FOREIGN KEY(user_id) REFERENCES members(user_id)
        )
        ''')

        # Duels table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS duels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenger_id INTEGER NOT NULL,
            challenged_id INTEGER NOT NULL,
            duel_type TEXT CHECK(duel_type IN ('sword', 'lance', 'trial_by_combat')),
            wager_amount INTEGER DEFAULT 0,
            status TEXT DEFAULT 'challenged',
            winner_id INTEGER,
            fight_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY(challenger_id) REFERENCES members(user_id),
            FOREIGN KEY(challenged_id) REFERENCES members(user_id),
            FOREIGN KEY(winner_id) REFERENCES members(user_id)
        )
        ''')

        # House resources (food, materials, etc.)
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS house_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_id INTEGER NOT NULL,
            resource_type TEXT CHECK(resource_type IN ('food', 'stone', 'wood', 'iron', 'horses', 'wine')),
            quantity INTEGER DEFAULT 0,
            quality INTEGER DEFAULT 50,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(house_id) REFERENCES alliances(id)
        )
        ''')

        # Trade offers table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS trade_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            offer_type TEXT CHECK(offer_type IN ('resource', 'soldiers', 'gold')),
            resource_type TEXT,
            quantity INTEGER NOT NULL,
            price_per_unit INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY(seller_id) REFERENCES alliances(id)
        )
        ''')

        # Trade agreements table  
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS trade_agreements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house1_id INTEGER NOT NULL,
            house2_id INTEGER NOT NULL,
            agreement_type TEXT DEFAULT 'trade_route',
            terms TEXT DEFAULT '{}',
            discount_percentage REAL DEFAULT 0.1,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY(house1_id) REFERENCES alliances(id),
            FOREIGN KEY(house2_id) REFERENCES alliances(id)
        )
        ''')

        # Trade transactions table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS trade_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            offer_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_cost INTEGER NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(buyer_id) REFERENCES alliances(id),
            FOREIGN KEY(seller_id) REFERENCES alliances(id),
            FOREIGN KEY(offer_id) REFERENCES trade_offers(id)
        )
        ''')

        # Marriages table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS marriages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            status TEXT DEFAULT 'proposed',
            married_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user1_id) REFERENCES members(user_id),
            FOREIGN KEY(user2_id) REFERENCES members(user_id)
        )
        ''')

        # Pregnancies table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS pregnancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mother_id INTEGER NOT NULL,
            father_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pregnant',
            due_date TIMESTAMP,
            birth_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(mother_id) REFERENCES members(user_id),
            FOREIGN KEY(father_id) REFERENCES members(user_id)
        )
        ''')

        # Children table
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mother_id INTEGER NOT NULL,
            father_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            gender TEXT CHECK(gender IN ('male', 'female')),
            birth_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            skills TEXT DEFAULT '{}',
            alive BOOLEAN DEFAULT 1,
            FOREIGN KEY(mother_id) REFERENCES members(user_id),
            FOREIGN KEY(father_id) REFERENCES members(user_id)
        )
        ''')

        # House debts table (Game of Thrones authentic debt system)
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS house_debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debtor_house_id INTEGER NOT NULL,
            creditor_house_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            interest_rate REAL DEFAULT 0.1,
            due_date TIMESTAMP,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(debtor_house_id) REFERENCES alliances(id),
            FOREIGN KEY(creditor_house_id) REFERENCES alliances(id)
        )
        ''')

        # Create warnings table for moderation
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create users table for compatibility
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            alliance_id INTEGER,
            username TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(alliance_id) REFERENCES alliances(id)
        )
        ''')

        self.conn.commit()
        logger.info("Database tables created successfully")

    def populate_default_data(self):
        """Populate database with default GOT houses if they don't exist"""

        houses_data = {
            "Lannister": {
                "region": "Batı", "gold": 2000000, "soldiers": 60000, "debt": 0,
                "special_ability": "Altın Gücü", "army_quality": 85
            },
            "Tyrell": {
                "region": "Ulaşım", "gold": 800000, "soldiers": 100000, "debt": 0,
                "special_ability": "Bahçe Gücü", "army_quality": 75
            },
            "Stark": {
                "region": "Kuzey", "gold": 120000, "soldiers": 45000, "debt": 200000,
                "special_ability": "Kış Savaşçısı", "army_quality": 80
            },
            "Arryn": {
                "region": "Vadi", "gold": 350000, "soldiers": 35000, "debt": 0,
                "special_ability": "Kartal Uçuşu", "army_quality": 78
            },
            "Baratheon": {
                "region": "Fırtına Toprakları", "gold": 80000, "soldiers": 30000, "debt": 6000000,
                "special_ability": "Savaş Öfkesi", "army_quality": 82
            },
            "Martell": {
                "region": "Dorne", "gold": 200000, "soldiers": 25000, "debt": 50000,
                "special_ability": "Çöl Savaşçısı", "army_quality": 70
            },
            "Tully": {
                "region": "Nehir Toprakları", "gold": 150000, "soldiers": 25000, "debt": 300000,
                "special_ability": "Nehir Kontrollü", "army_quality": 65
            },
            "Greyjoy": {
                "region": "Demir Adalar", "gold": 60000, "soldiers": 20000, "debt": 150000,
                "special_ability": "Deniz Lordluğu", "army_quality": 72
            },
            "Targaryen": {
                "region": "Dragonstone", "gold": 30000, "soldiers": 8000, "debt": 100000,
                "special_ability": "Eski Valyria Mirası", "army_quality": 90
            },
            "Bolton": {
                "region": "Dreadfort", "gold": 40000, "soldiers": 12000, "debt": 200000,
                "special_ability": "Korku Tacticsi", "army_quality": 75
            }
        }

        for house_name, house_data in houses_data.items():
            try:
                self.c.execute('''
                INSERT OR IGNORE INTO alliances (name, house_type, region, gold, soldiers, debt, special_ability, army_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (house_name, house_name, house_data["region"], house_data["gold"], 
                      house_data["soldiers"], house_data["debt"], house_data["special_ability"], house_data["army_quality"]))

                # Initialize army resources for each house
                self.c.execute('SELECT id FROM alliances WHERE name = ?', (house_name,))
                house_result = self.c.fetchone()
                if house_result:
                    house_id = house_result[0]

                    # Check if army resources already exist
                    self.c.execute('SELECT id FROM army_resources WHERE house_id = ?', (house_id,))
                    if not self.c.fetchone():
                        # Initialize based on house wealth and characteristics
                        base_resources = self._get_house_base_resources(house_name, house_data)
                        self.c.execute('''
                        INSERT INTO army_resources 
                        (house_id, food_supplies, weapons_quality, armor_quality, siege_weapons, 
                         cavalry, archers, infantry, navy_ships, army_training, morale)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (house_id, base_resources['food'], base_resources['weapons'], 
                             base_resources['armor'], base_resources['siege'], base_resources['cavalry'],
                             base_resources['archers'], base_resources['infantry'], base_resources['navy'],
                             base_resources['training'], base_resources['morale']))

                    # Initialize basic resources
                    resource_types = ['food', 'stone', 'wood', 'iron', 'horses', 'wine']
                    for resource in resource_types:
                        self.c.execute('SELECT id FROM house_resources WHERE house_id = ? AND resource_type = ?', 
                                     (house_id, resource))
                        if not self.c.fetchone():
                            base_quantity = self._get_base_resource_quantity(house_name, resource, house_data)
                            self.c.execute('''
                            INSERT INTO house_resources (house_id, resource_type, quantity, quality)
                            VALUES (?, ?, ?, ?)
                            ''', (house_id, resource, base_quantity, 60))
            except sqlite3.IntegrityError:
                pass  # House already exists

        self.conn.commit()

        # Add realistic debt relationships between houses
        try:
            debt_relationships = [
                # (Debtor, Creditor, Amount, Interest Rate, Days)
                ("Baratheon", "Lannister", 6000000, 0.15, 365),  # Crown debt to Lannisters
                ("Stark", "Lannister", 500000, 0.12, 300),       # War loans
                ("Targaryen", "Tyrell", 200000, 0.10, 200),      # Exile support
                ("Greyjoy", "Lannister", 300000, 0.18, 180),     # Rebellion reparations  
                ("Tully", "Tyrell", 800000, 0.14, 400),         # Agricultural loans
                ("Bolton", "Lannister", 400000, 0.16, 250),     # Military support
                ("Martell", "Tyrell", 100000, 0.08, 150),       # Trade agreements
            ]

            for debtor_name, creditor_name, amount, interest_rate, days in debt_relationships:
                # Get house IDs
                self.c.execute('SELECT id FROM alliances WHERE name = ?', (debtor_name,))
                debtor_result = self.c.fetchone()
                self.c.execute('SELECT id FROM alliances WHERE name = ?', (creditor_name,))
                creditor_result = self.c.fetchone()

                if debtor_result and creditor_result:
                    debtor_id = debtor_result[0]
                    creditor_id = creditor_result[0]

                    # Check if debt already exists
                    self.c.execute('SELECT id FROM house_debts WHERE debtor_house_id = ? AND creditor_house_id = ?', 
                                  (debtor_id, creditor_id))
                    if not self.c.fetchone():
                        # Create the debt
                        due_date = (datetime.now() + timedelta(days=days)).isoformat()
                        self.c.execute('''
                        INSERT INTO house_debts (debtor_house_id, creditor_house_id, amount, due_date, interest_rate)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (debtor_id, creditor_id, amount, due_date, interest_rate))
                        logger.info(f"Debt created: {debtor_name} owes {creditor_name} {amount:,} gold")

            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating default debts: {e}")

        logger.info("Default house data populated")

    def _get_house_base_resources(self, house_name, house_data):
        """Get base army resources for a house based on its characteristics"""
        wealth_factor = house_data["gold"] / 100000  # Scale based on wealth
        soldier_count = house_data["soldiers"]

        base = {
            'food': max(500, int(soldier_count * 0.8)),
            'weapons': house_data["army_quality"],
            'armor': house_data["army_quality"] - 5,
            'siege': max(0, int(wealth_factor * 2)),
            'cavalry': max(0, int(soldier_count * 0.15)),
            'archers': max(0, int(soldier_count * 0.25)),
            'infantry': max(0, int(soldier_count * 0.6)),
            'navy': 0,
            'training': house_data["army_quality"] - 10,
            'morale': 70
        }

        # House-specific adjustments
        if house_name == "Lannister":
            base['weapons'] += 10
            base['armor'] += 10
            base['siege'] += 5
        elif house_name == "Stark":
            base['morale'] += 15
            base['training'] += 10
        elif house_name == "Tyrell":
            base['food'] += 2000
            base['cavalry'] += int(soldier_count * 0.1)
        elif house_name == "Greyjoy":
            base['navy'] = max(50, int(wealth_factor * 10))
            base['archers'] = max(0, int(soldier_count * 0.1))
        elif house_name == "Arryn":
            base['training'] += 15
            base['morale'] += 10
        elif house_name == "Baratheon":
            base['weapons'] += 5
            base['siege'] += 3
        elif house_name == "Martell":
            base['archers'] += int(soldier_count * 0.2)
        elif house_name == "Targaryen":
            base['morale'] += 20
            base['training'] += 15

        return base

    def _get_base_resource_quantity(self, house_name, resource_type, house_data):
        """Get base resource quantity for a house"""
        wealth_factor = house_data["gold"] / 50000

        base_quantities = {
            'food': max(1000, int(wealth_factor * 500)),
            'stone': max(200, int(wealth_factor * 100)),
            'wood': max(300, int(wealth_factor * 150)),
            'iron': max(100, int(wealth_factor * 50)),
            'horses': max(50, int(wealth_factor * 25)),
            'wine': max(100, int(wealth_factor * 75))
        }

        base = base_quantities.get(resource_type, 100)

        # House-specific bonuses
        if house_name == "Tyrell" and resource_type == "food":
            base *= 3
        elif house_name == "Lannister" and resource_type in ["iron", "stone"]:
            base *= 2
        elif house_name == "Arryn" and resource_type == "stone":
            base *= 2
        elif house_name == "Greyjoy" and resource_type == "wood":
            base *= 1.5
        elif house_name == "Stark" and resource_type == "wood":
            base *= 2

        return int(base)

    def get_user_alliance(self, user_id):
        """Get user's alliance information"""
        try:
            self.c.execute('''
            SELECT a.*, m.role FROM alliances a 
            JOIN members m ON a.id = m.alliance_id 
            WHERE m.user_id = ?
            ''', (user_id,))
            return self.c.fetchone()
        except Exception as e:
            logger.error(f"Error getting user alliance: {e}")
            return None

    def get_alliance_by_id(self, alliance_id):
        """Get alliance by ID"""
        try:
            self.c.execute('SELECT * FROM alliances WHERE id = ?', (alliance_id,))
            return self.c.fetchone()
        except Exception as e:
            logger.error(f"Error getting alliance by ID: {e}")
            return None

    def get_alliance_by_name(self, name):
        """Get alliance by name"""
        try:
            self.c.execute('SELECT * FROM alliances WHERE name = ?', (name,))
            return self.c.fetchone()
        except Exception as e:
            logger.error(f"Error getting alliance by name: {e}")
            return None

    def get_alliance_members(self, alliance_id):
        """Get all members of an alliance"""
        try:
            self.c.execute('''
            SELECT m.*, ac.character_name FROM members m 
            LEFT JOIN asoiaf_characters ac ON m.user_id = ac.user_id
            WHERE m.alliance_id = ?
            ORDER BY m.role DESC, m.joined_at ASC
            ''', (alliance_id,))
            return self.c.fetchall()
        except Exception as e:
            logger.error(f"Error getting alliance members: {e}")
            return []

    def update_alliance_resources(self, alliance_id, gold_change=0, soldiers_change=0):
        """Update alliance resources"""
        try:
            self.c.execute('''
            UPDATE alliances 
            SET gold = max(0, gold + ?), soldiers = max(0, soldiers + ?)
            WHERE id = ?
            ''', (gold_change, soldiers_change, alliance_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating alliance resources: {e}")
            return False

    def create_war(self, attacker_id, defender_id, weather='normal', terrain='ova'):
        """Create a new war"""
        try:
            self.c.execute('''
            INSERT INTO wars (attacker_id, defender_id, weather, terrain)
            VALUES (?, ?, ?, ?)
            ''', (attacker_id, defender_id, weather, terrain))
            war_id = self.c.lastrowid
            self.conn.commit()
            return war_id
        except Exception as e:
            logger.error(f"Error creating war: {e}")
            return None

    def get_active_wars(self, alliance_id=None):
        """Get active wars, optionally filtered by alliance"""
        try:
            if alliance_id:
                self.c.execute('''
                SELECT * FROM wars 
                WHERE (attacker_id = ? OR defender_id = ?) AND status = 'active'
                ''', (alliance_id, alliance_id))
            else:
                self.c.execute("SELECT * FROM wars WHERE status = 'active'")
            return self.c.fetchall()
        except Exception as e:
            logger.error(f"Error getting active wars: {e}")
            return []

    def end_war(self, war_id, winner_id):
        """End a war with a winner"""
        try:
            self.c.execute('''
            UPDATE wars 
            SET status = 'ended', winner_id = ?, end_time = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (winner_id, war_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error ending war: {e}")
            return False

    def add_battle_log(self, war_id, turn_number, attacker_action, defender_action, result, attacker_damage=0, defender_damage=0):
        """Add a battle log entry"""
        try:
            self.c.execute('''
            INSERT INTO battle_logs (war_id, turn_number, attacker_action, defender_action, result, attacker_damage, defender_damage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (war_id, turn_number, attacker_action, defender_action, result, attacker_damage, defender_damage))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding battle log: {e}")
            return False

    def get_income_sources(self, house_id):
        """Get all income sources for a house"""
        try:
            self.c.execute('''
            SELECT * FROM income_sources 
            WHERE house_id = ? OR seized_by = ?
            ORDER BY income_per_minute DESC
            ''', (house_id, house_id))
            return self.c.fetchall()
        except Exception as e:
            logger.error(f"Error getting income sources: {e}")
            return []

    def add_income_source(self, house_id, source_type, name, region, income_per_minute, cost):
        """Add a new income source"""
        try:
            self.c.execute('''
            INSERT INTO income_sources (house_id, source_type, name, region, income_per_minute, cost)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (house_id, source_type, name, region, income_per_minute, cost))
            self.conn.commit()
            return self.c.lastrowid
        except Exception as e:
            logger.error(f"Error adding income source: {e}")
            return None

    def create_marriage(self, user1_id, user2_id):
        """Create a marriage between two users"""
        try:
            # Insert marriage record
            self.c.execute('''
            INSERT INTO marriages (user1_id, user2_id)
            VALUES (?, ?)
            ''', (user1_id, user2_id))

            # Update member records
            self.c.execute('UPDATE members SET married_to = ? WHERE user_id = ?', (user2_id, user1_id))
            self.c.execute('UPDATE members SET married_to = ? WHERE user_id = ?', (user1_id, user2_id))

            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating marriage: {e}")
            return False

    def get_user_member_data(self, user_id):
        """Get complete member data for a user"""
        try:
            self.c.execute('SELECT * FROM members WHERE user_id = ?', (user_id,))
            return self.c.fetchone()
        except Exception as e:
            logger.error(f"Error getting member data: {e}")
            return None

    def close(self):
        """Close database connection"""
        try:
            self.conn.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")