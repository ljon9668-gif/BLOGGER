import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import os

class Database:
    def __init__(self, db_path: str = "blog_migration.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_url TEXT,
                rewritten_title TEXT,
                rewritten_content TEXT,
                meta_description TEXT,
                images TEXT,
                tags TEXT,
                suggested_tags TEXT,
                status TEXT DEFAULT 'extracted',
                scheduled_time TIMESTAMP,
                published_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_source_id ON posts(source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time ON posts(scheduled_time)')
        
        conn.commit()
        conn.close()
    
    def add_source(self, url: str, name: str) -> bool:
        """Add a new source blog"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO sources (url, name) VALUES (?, ?)',
                (url, name)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Get all source blogs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sources ORDER BY created_at DESC')
        sources = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sources
    
    def delete_source(self, source_id: int):
        """Delete a source and all its posts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sources WHERE id = ?', (source_id,))
        conn.commit()
        conn.close()
    
    def add_post(self, source_id: int, title: str, content: str, source_url: str,
                 images: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> int:
        """Add a new post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        images_json = json.dumps(images) if images else '[]'
        tags_json = json.dumps(tags) if tags else '[]'
        
        cursor.execute('''
            INSERT INTO posts (source_id, title, content, source_url, images, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source_id, title, content, source_url, images_json, tags_json))
        
        post_id = cursor.lastrowid
        if post_id is None:
            conn.close()
            raise Exception("Failed to insert post - no ID returned")
        
        conn.commit()
        conn.close()
        return post_id
    
    def is_duplicate(self, title: str, source_url: str) -> bool:
        """Check if post already exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) as count FROM posts WHERE title = ? OR source_url = ?',
            (title, source_url)
        )
        result = cursor.fetchone()
        conn.close()
        return result['count'] > 0
    
    def get_posts_by_source(self, source_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get posts from a specific source"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                'SELECT * FROM posts WHERE source_id = ? AND status = ? ORDER BY created_at DESC',
                (source_id, status)
            )
        else:
            cursor.execute(
                'SELECT * FROM posts WHERE source_id = ? ORDER BY created_at DESC',
                (source_id,)
            )
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for post in posts:
            post['images'] = json.loads(post['images']) if post['images'] else []
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
            post['suggested_tags'] = json.loads(post['suggested_tags']) if post['suggested_tags'] else []
        
        return posts
    
    def get_posts_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC LIMIT ?',
            (status, limit)
        )
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for post in posts:
            post['images'] = json.loads(post['images']) if post['images'] else []
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
            post['suggested_tags'] = json.loads(post['suggested_tags']) if post['suggested_tags'] else []
        
        return posts
    
    def get_all_posts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all posts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY created_at DESC LIMIT ?', (limit,))
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for post in posts:
            post['images'] = json.loads(post['images']) if post['images'] else []
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
            post['suggested_tags'] = json.loads(post['suggested_tags']) if post['suggested_tags'] else []
        
        return posts
    
    def update_post_rewritten(self, post_id: int, rewritten_title: str,
                             rewritten_content: str, meta_description: Optional[str] = None,
                             suggested_tags: Optional[List[str]] = None):
        """Update post with rewritten content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        suggested_tags_json = json.dumps(suggested_tags) if suggested_tags else '[]'
        
        cursor.execute('''
            UPDATE posts 
            SET rewritten_title = ?, 
                rewritten_content = ?, 
                meta_description = ?,
                suggested_tags = ?,
                status = 'rewritten',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (rewritten_title, rewritten_content, meta_description, suggested_tags_json, post_id))
        
        conn.commit()
        conn.close()
    
    def update_post_scheduled(self, post_id: int, scheduled_time: datetime):
        """Update post with scheduled time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE posts 
            SET scheduled_time = ?, 
                status = 'scheduled',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (scheduled_time.isoformat(), post_id))
        conn.commit()
        conn.close()
    
    def update_post_published(self, post_id: int, published_url: str):
        """Update post as published"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE posts 
            SET published_url = ?, 
                status = 'published',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (published_url, post_id))
        conn.commit()
        conn.close()
    
    def update_post_failed(self, post_id: int, error_message: str):
        """Mark post as failed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE posts 
            SET status = 'failed',
                meta_description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (error_message, post_id))
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get migration statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM sources')
        total_sources = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM posts WHERE status = 'extracted'")
        total_extracted = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM posts WHERE status = 'published'")
        total_published = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM posts WHERE status IN ('extracted', 'rewritten', 'scheduled')")
        total_pending = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_sources': total_sources,
            'total_extracted': total_extracted,
            'total_published': total_published,
            'total_pending': total_pending
        }
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, s.name as source_name 
            FROM posts p 
            LEFT JOIN sources s ON p.source_id = s.id 
            ORDER BY p.updated_at DESC 
            LIMIT ?
        ''', (limit,))
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return posts
    
    def get_source_post_count(self, source_id: int) -> int:
        """Get post count for a source"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE source_id = ?', (source_id,))
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def clear_all_data(self):
        """Clear all migration data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM posts')
        cursor.execute('DELETE FROM sources')
        conn.commit()
        conn.close()
