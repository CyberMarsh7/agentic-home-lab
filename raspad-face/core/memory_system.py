"""
Kokoro Memory System
Persistent, learning memory that grows with the user
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class KokoroMemory:
    def __init__(self, db_path: str = "/mnt/data/kokoro/memory.db"):
        """Initialize Kokoro's persistent memory"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        # Interactions table
        c.execute('''CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            user_input TEXT,
            kokoro_response TEXT,
            emotion_detected TEXT,
            confidence REAL,
            outcome TEXT
        )''')

        # User preferences
        c.execute('''CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated TEXT
        )''')

        # Learned patterns
        c.execute('''CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            data TEXT,
            frequency INTEGER,
            last_observed TEXT
        )''')

        # Personality traits (user's character)
        c.execute('''CREATE TABLE IF NOT EXISTS traits (
            trait TEXT PRIMARY KEY,
            value REAL,
            updated TEXT
        )''')

        conn.commit()
        conn.close()
        logger.info("Memory system initialized")

    def record_interaction(self, user_input: str, kokoro_response: str,
                          emotion: str, confidence: float, outcome: str = "success"):
        """Record an interaction"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('''INSERT INTO interactions
                     (timestamp, user_input, kokoro_response, emotion_detected, confidence, outcome)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), user_input, kokoro_response, emotion, confidence, outcome))

        conn.commit()
        conn.close()
        logger.info(f"Recorded interaction: {emotion} ({confidence:.2f})")

    def get_interaction_history(self, limit: int = 50) -> List[Dict]:
        """Get recent interactions"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('SELECT * FROM interactions ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()

        return [
            {
                'timestamp': row[1],
                'input': row[2],
                'response': row[3],
                'emotion': row[4],
                'confidence': row[5],
                'outcome': row[6]
            }
            for row in rows
        ]

    def set_preference(self, key: str, value: str):
        """Store a user preference"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('''INSERT OR REPLACE INTO preferences (key, value, updated)
                     VALUES (?, ?, ?)''',
                  (key, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()
        logger.info(f"Preference set: {key} = {value}")

    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = c.fetchone()
        conn.close()

        return row[0] if row else None

    def learn_pattern(self, pattern_type: str, data: Dict):
        """Learn a behavioral pattern"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        data_json = json.dumps(data)

        # Check if pattern exists
        c.execute('SELECT id, frequency FROM patterns WHERE pattern_type = ? AND data = ?',
                  (pattern_type, data_json))
        row = c.fetchone()

        if row:
            # Update frequency
            c.execute('UPDATE patterns SET frequency = ?, last_observed = ? WHERE id = ?',
                      (row[1] + 1, datetime.now().isoformat(), row[0]))
        else:
            # New pattern
            c.execute('''INSERT INTO patterns (pattern_type, data, frequency, last_observed)
                         VALUES (?, ?, ?, ?)''',
                      (pattern_type, data_json, 1, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_common_patterns(self, pattern_type: str, limit: int = 10) -> List[Dict]:
        """Get most common patterns"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('''SELECT data, frequency FROM patterns
                     WHERE pattern_type = ?
                     ORDER BY frequency DESC LIMIT ?''',
                  (pattern_type, limit))
        rows = c.fetchall()
        conn.close()

        return [
            {'pattern': json.loads(row[0]), 'frequency': row[1]}
            for row in rows
        ]

    def set_trait(self, trait: str, value: float):
        """Set a personality trait about the user"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('''INSERT OR REPLACE INTO traits (trait, value, updated)
                     VALUES (?, ?, ?)''',
                  (trait, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_trait(self, trait: str) -> Optional[float]:
        """Get a personality trait value"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('SELECT value FROM traits WHERE trait = ?', (trait,))
        row = c.fetchone()
        conn.close()

        return row[0] if row else None

    def get_all_traits(self) -> Dict[str, float]:
        """Get all learned traits"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('SELECT trait, value FROM traits')
        rows = c.fetchall()
        conn.close()

        return {row[0]: row[1] for row in rows}

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()

        c.execute('SELECT COUNT(*) FROM interactions')
        total_interactions = c.fetchone()[0]

        c.execute('SELECT emotion_detected, COUNT(*) FROM interactions GROUP BY emotion_detected')
        emotions = {row[0]: row[1] for row in c.fetchall()}

        c.execute('SELECT COUNT(*) FROM patterns')
        learned_patterns = c.fetchone()[0]

        conn.close()

        return {
            'total_interactions': total_interactions,
            'emotions_detected': emotions,
            'learned_patterns': learned_patterns,
            'traits_learned': len(self.get_all_traits())
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    mem = KokoroMemory()

    # Record some interactions
    mem.record_interaction("turn on the lights", "Turning on the lights now", "happy", 0.85)
    mem.record_interaction("I'm frustrated", "I understand. Let me help.", "frustrated", 0.92)

    # Set preferences
    mem.set_preference("favorite_color", "blue")
    mem.set_preference("preferred_time", "morning")

    # Learn traits about the user
    mem.set_trait("visionary", 0.9)
    mem.set_trait("determined", 0.85)
    mem.set_trait("creative", 0.88)

    # Get stats
    print("Memory Stats:", mem.get_stats())
    print("Traits:", mem.get_all_traits())
