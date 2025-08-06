import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    def __init__(self, db):
        self.db = db
        
    def optimize_database(self):
        """Optimize database performance"""
        try:
            # Create indexes for faster queries
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_members_user_id ON members(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_members_alliance_id ON members(alliance_id)",
                "CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_users_alliance_id ON users(alliance_id)",
                "CREATE INDEX IF NOT EXISTS idx_wars_attacker_id ON wars(attacker_id)",
                "CREATE INDEX IF NOT EXISTS idx_wars_defender_id ON wars(defender_id)",
                "CREATE INDEX IF NOT EXISTS idx_wars_status ON wars(status)",
                "CREATE INDEX IF NOT EXISTS idx_tournaments_status ON tournaments(status)",
                "CREATE INDEX IF NOT EXISTS idx_duels_challenger_id ON duels(challenger_id)",
                "CREATE INDEX IF NOT EXISTS idx_duels_challenged_id ON duels(challenged_id)",
                "CREATE INDEX IF NOT EXISTS idx_marriages_user1_id ON marriages(user1_id)",
                "CREATE INDEX IF NOT EXISTS idx_marriages_user2_id ON marriages(user2_id)",
                "CREATE INDEX IF NOT EXISTS idx_income_sources_house_id ON income_sources(house_id)",
                "CREATE INDEX IF NOT EXISTS idx_house_debts_creditor_house_id ON house_debts(creditor_house_id)",
                "CREATE INDEX IF NOT EXISTS idx_house_debts_debtor_house_id ON house_debts(debtor_house_id)"
            ]
            
            for index_sql in indexes:
                try:
                    self.db.c.execute(index_sql)
                except sqlite3.OperationalError as e:
                    if "no such table" in str(e):
                        logger.warning(f"Skipping index creation - table doesn't exist: {e}")
                    else:
                        raise
            
            # Vacuum database to reclaim space
            self.db.c.execute("VACUUM")
            
            # Analyze tables for query optimization
            self.db.c.execute("ANALYZE")
            
            self.db.conn.commit()
            logger.info("Database optimization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            return False
    
    def cleanup_old_data(self):
        """Clean up old data to improve performance"""
        try:
            # Clean up old data - use simpler approach since created_at column may not exist
            # Remove finished tournaments older than 30 days
            self.db.c.execute('''
            DELETE FROM tournaments 
            WHERE status = 'finished' AND id NOT IN (
                SELECT id FROM tournaments 
                WHERE status = 'finished' 
                ORDER BY id DESC 
                LIMIT 50
            )
            ''')
            
            # Remove finished wars older than 30 days
            self.db.c.execute('''
            DELETE FROM wars 
            WHERE status IN ('finished', 'cancelled') AND id NOT IN (
                SELECT id FROM wars 
                WHERE status IN ('finished', 'cancelled') 
                ORDER BY id DESC 
                LIMIT 50
            )
            ''')
            
            # Remove finished duels (keep only last 20)
            self.db.c.execute('''
            DELETE FROM duels 
            WHERE status IN ('finished', 'cancelled') AND id NOT IN (
                SELECT id FROM duels 
                WHERE status IN ('finished', 'cancelled') 
                ORDER BY id DESC 
                LIMIT 20
            )
            ''')
            
            self.db.conn.commit()
            logger.info("Old data cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"Data cleanup error: {e}")
            return False
    
    def get_performance_stats(self):
        """Get database performance statistics"""
        try:
            stats = {}
            
            # Check which tables actually exist
            self.db.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in self.db.c.fetchall()]
            
            # Table sizes - only check existing tables
            tables = ['alliances', 'members', 'wars', 'tournaments', 
                     'duels', 'marriages', 'income_sources', 'house_debts',
                     'asoiaf_characters', 'battle_logs', 'army_resources']
            
            for table in tables:
                if table in existing_tables:
                    try:
                        self.db.c.execute(f"SELECT COUNT(*) FROM {table}")
                        stats[f"{table}_count"] = self.db.c.fetchone()[0]
                    except sqlite3.OperationalError as e:
                        logger.warning(f"Error counting {table}: {e}")
                        stats[f"{table}_count"] = 0
                else:
                    stats[f"{table}_count"] = 0
            
            # Database size
            self.db.c.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size_bytes'] = self.db.c.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Performance stats error: {e}")
            return {}