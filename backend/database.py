# Database operations for AI-Powered Communication Assistant
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from config import config

class DatabaseManager:
    """Manages SQLite database operations for email system"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.database.db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory and timeout"""
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                thread_id TEXT,
                sender TEXT NOT NULL,
                recipients TEXT NOT NULL,  -- JSON string
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                sentiment TEXT DEFAULT 'neutral',  -- positive, negative, neutral
                sentiment_score REAL DEFAULT 0.0,  -- -1 to 1
                priority TEXT DEFAULT 'normal',  -- urgent, normal, low
                status TEXT DEFAULT 'unread',  -- unread, read, resolved
                labels TEXT,  -- JSON string
                attachments TEXT,  -- JSON string
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI Responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id INTEGER NOT NULL,
                generated_response TEXT NOT NULL,
                edited_response TEXT,
                sent_status TEXT DEFAULT 'draft',  -- draft, sent, failed
                confidence_score REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sent_at DATETIME,
                FOREIGN KEY (email_id) REFERENCES emails (id)
            )
        ''')
        
        # Analytics table for daily statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                total_emails INTEGER DEFAULT 0,
                urgent_emails INTEGER DEFAULT 0,
                resolved_emails INTEGER DEFAULT 0,
                positive_sentiment INTEGER DEFAULT 0,
                negative_sentiment INTEGER DEFAULT 0,
                neutral_sentiment INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0.0,  -- in hours
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table for configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_email(self, email_data: Dict) -> int:
        """Insert new email into database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO emails (
                message_id, thread_id, sender, recipients, subject, body,
                timestamp, sentiment, sentiment_score, priority, labels, attachments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_data['message_id'],
            email_data.get('thread_id'),
            email_data['sender'],
            json.dumps(email_data['recipients']),
            email_data['subject'],
            email_data['body'],
            email_data['timestamp'],
            email_data.get('sentiment', 'neutral'),
            email_data.get('sentiment_score', 0.0),
            email_data.get('priority', 'normal'),
            json.dumps(email_data.get('labels', [])),
            json.dumps(email_data.get('attachments', []))
        ))
        
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return email_id
    
    def get_emails(self, status: str = None, priority: str = None, limit: int = None) -> List[Dict]:
        """Retrieve emails with optional filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM emails"
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if priority:
            conditions.append("priority = ?")
            params.append(priority)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to dictionaries and parse JSON fields
        emails = []
        for row in rows:
            email = dict(row)
            email['recipients'] = json.loads(email['recipients'])
            email['labels'] = json.loads(email['labels']) if email['labels'] else []
            email['attachments'] = json.loads(email['attachments']) if email['attachments'] else []
            emails.append(email)
        
        return emails
    
    def update_email_status(self, email_id: int, status: str):
        """Update email status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE emails 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, email_id))
        
        conn.commit()
        conn.close()
    
    def insert_response(self, response_data: Dict) -> int:
        """Insert AI-generated response"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO responses (
                email_id, generated_response, confidence_score
            ) VALUES (?, ?, ?)
        ''', (
            response_data['email_id'],
            response_data['generated_response'],
            response_data.get('confidence_score', 0.0)
        ))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return response_id
    
    def get_responses(self, email_id: int = None) -> List[Dict]:
        """Get AI responses"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if email_id:
            cursor.execute('''
                SELECT r.*, e.subject, e.sender 
                FROM responses r
                JOIN emails e ON r.email_id = e.id
                WHERE r.email_id = ?
                ORDER BY r.created_at DESC
            ''', (email_id,))
        else:
            cursor.execute('''
                SELECT r.*, e.subject, e.sender 
                FROM responses r
                JOIN emails e ON r.email_id = e.id
                ORDER BY r.created_at DESC
                LIMIT 50
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_response_status(self, response_id: int, status: str, edited_response: str = None):
        """Update response status and edited content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if edited_response:
            cursor.execute('''
                UPDATE responses 
                SET sent_status = ?, edited_response = ?, sent_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, edited_response, response_id))
        else:
            cursor.execute('''
                UPDATE responses 
                SET sent_status = ?, sent_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, response_id))
        
        conn.commit()
        conn.close()
    
    def get_analytics_data(self, days: int = 7) -> Dict:
        """Get analytics data for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Total emails by date
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM emails 
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (start_date,))
        
        daily_emails = cursor.fetchall()
        
        # Sentiment distribution
        cursor.execute('''
            SELECT sentiment, COUNT(*) as count
            FROM emails
            WHERE DATE(timestamp) >= ?
            GROUP BY sentiment
        ''', (start_date,))
        
        sentiment_data = cursor.fetchall()
        
        # Priority distribution
        cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM emails
            WHERE DATE(timestamp) >= ?
            GROUP BY priority
        ''', (start_date,))
        
        priority_data = cursor.fetchall()
        
        # Response statistics
        cursor.execute('''
            SELECT sent_status, COUNT(*) as count
            FROM responses r
            JOIN emails e ON r.email_id = e.id
            WHERE DATE(e.timestamp) >= ?
            GROUP BY sent_status
        ''', (start_date,))
        
        response_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'daily_emails': [dict(row) for row in daily_emails],
            'sentiment_distribution': [dict(row) for row in sentiment_data],
            'priority_distribution': [dict(row) for row in priority_data],
            'response_statistics': [dict(row) for row in response_stats]
        }
    
    def get_urgent_emails_count(self) -> int:
        """Get count of urgent unresolved emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM emails
            WHERE priority = 'urgent' AND status != 'resolved'
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] if result else 0
    
    def search_emails(self, query: str, limit: int = 50) -> List[Dict]:
        """Search emails by subject or body content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_query = f"%{query}%"
        cursor.execute('''
            SELECT * FROM emails
            WHERE subject LIKE ? OR body LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (search_query, search_query, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        emails = []
        for row in rows:
            email = dict(row)
            email['recipients'] = json.loads(email['recipients'])
            email['labels'] = json.loads(email['labels']) if email['labels'] else []
            emails.append(email)
        
        return emails
    
    def get_email_by_message_id(self, message_id: str) -> Optional[Dict]:
        """Get email by message ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM emails WHERE message_id = ?
        ''', (message_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            email = dict(row)
            email['recipients'] = json.loads(email['recipients'])
            email['labels'] = json.loads(email['labels']) if email['labels'] else []
            email['attachments'] = json.loads(email['attachments']) if email['attachments'] else []
            return email
        
        return None
    
    def add_email(self, message_id: str, thread_id: str, sender: str, subject: str, 
                  body: str, timestamp: datetime, priority: str = 'normal', 
                  sentiment: str = 'neutral', sentiment_score: float = 0.0,
                  key_emotions: List[str] = None, confidence: float = 0.0) -> int:
        """Add email with AI analysis results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO emails (
                message_id, thread_id, sender, recipients, subject, body,
                timestamp, priority, sentiment, sentiment_score, labels, attachments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_id,
            thread_id,
            sender,
            json.dumps({'to': sender}),  # Basic recipients structure
            subject,
            body,
            timestamp,
            priority,
            sentiment,
            sentiment_score,
            json.dumps(key_emotions or []),
            json.dumps([])  # Empty attachments for now
        ))
        
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return email_id
    
    def add_response(self, email_id: int, generated_response: str, 
                    confidence_score: float = 0.0, context_considered: Dict = None) -> int:
        """Add AI-generated response"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO responses (
                email_id, generated_response, confidence_score
            ) VALUES (?, ?, ?)
        ''', (
            email_id,
            generated_response,
            confidence_score
        ))
        
        response_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return response_id

# Global database instance
db = DatabaseManager()