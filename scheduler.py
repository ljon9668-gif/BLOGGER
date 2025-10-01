from datetime import datetime, timedelta, time
from typing import List, Dict, Any
from database import Database

class PostScheduler:
    def __init__(self, db: Database):
        self.db = db
    
    def create_schedule(self, posts: List[Dict[str, Any]], 
                       start_date: Any, start_time: time,
                       posts_per_day: int = 1) -> List[Dict[str, Any]]:
        """Create a publishing schedule for posts"""
        
        schedule = []
        current_datetime = datetime.combine(start_date, start_time)
        
        for i, post in enumerate(posts):
            # Calculate scheduled time
            days_offset = i // posts_per_day
            post_index_in_day = i % posts_per_day
            
            # Add hours between posts on the same day (e.g., 2 hours apart)
            hours_offset = post_index_in_day * 2
            
            scheduled_time = current_datetime + timedelta(days=days_offset, hours=hours_offset)
            
            schedule.append({
                'post_id': post['id'],
                'title': post.get('rewritten_title') or post['title'],
                'scheduled_time': scheduled_time,
                'status': 'scheduled'
            })
        
        return schedule
    
    def get_due_posts(self, current_time: datetime = None) -> List[Dict[str, Any]]:
        """Get posts that are due for publishing"""
        
        if current_time is None:
            current_time = datetime.now()
        
        # This would query the database for posts scheduled before current_time
        # For now, returning empty list as this would be used in a background worker
        return []
    
    def reschedule_post(self, post_id: int, new_time: datetime):
        """Reschedule a post to a new time"""
        
        self.db.update_post_scheduled(post_id, new_time)
    
    def calculate_next_available_slot(self, start_time: datetime,
                                      posts_per_day: int,
                                      hours_between_posts: int = 2) -> datetime:
        """Calculate the next available publishing slot"""
        
        # Get all scheduled posts
        scheduled_posts = self.db.get_posts_by_status('scheduled')
        
        if not scheduled_posts:
            return start_time
        
        # Find the latest scheduled time
        latest_time = start_time
        for post in scheduled_posts:
            if post.get('scheduled_time'):
                post_time = datetime.fromisoformat(post['scheduled_time'])
                if post_time > latest_time:
                    latest_time = post_time
        
        # Add interval for next slot
        return latest_time + timedelta(hours=hours_between_posts)
