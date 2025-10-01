import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        """Initialize Supabase connection"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")

        self.client: Client = create_client(supabase_url, supabase_key)

    def add_source(self, url: str, name: str) -> bool:
        """Add a new source blog"""
        try:
            self.client.table('sources').insert({
                'url': url,
                'name': name
            }).execute()
            return True
        except Exception as e:
            print(f"Error adding source: {str(e)}")
            return False

    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Get all source blogs"""
        try:
            response = self.client.table('sources').select('*').order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting sources: {str(e)}")
            return []

    def delete_source(self, source_id: str):
        """Delete a source and all its posts"""
        try:
            self.client.table('sources').delete().eq('id', source_id).execute()
        except Exception as e:
            print(f"Error deleting source: {str(e)}")

    def add_post(self, source_id: str, title: str, content: str, source_url: str,
                 images: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> str:
        """Add a new post"""
        try:
            response = self.client.table('posts').insert({
                'source_id': source_id,
                'title': title,
                'content': content,
                'source_url': source_url,
                'images': images or [],
                'tags': tags or [],
                'status': 'extracted'
            }).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]['id']
            raise Exception("Failed to insert post - no ID returned")

        except Exception as e:
            print(f"Error adding post: {str(e)}")
            raise

    def is_duplicate(self, title: str, source_url: str) -> bool:
        """Check if post already exists"""
        try:
            response = self.client.table('posts')\
                .select('id')\
                .or_(f'title.eq.{title},source_url.eq.{source_url}')\
                .limit(1)\
                .execute()

            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking duplicate: {str(e)}")
            return False

    def get_posts_by_source(self, source_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get posts from a specific source"""
        try:
            query = self.client.table('posts').select('*').eq('source_id', source_id)

            if status:
                query = query.eq('status', status)

            response = query.order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting posts by source: {str(e)}")
            return []

    def get_posts_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts by status"""
        try:
            response = self.client.table('posts')\
                .select('*')\
                .eq('status', status)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            return response.data
        except Exception as e:
            print(f"Error getting posts by status: {str(e)}")
            return []

    def get_all_posts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all posts"""
        try:
            response = self.client.table('posts')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            return response.data
        except Exception as e:
            print(f"Error getting all posts: {str(e)}")
            return []

    def update_post_rewritten(self, post_id: str, rewritten_title: str,
                             rewritten_content: str, meta_description: Optional[str] = None,
                             suggested_tags: Optional[List[str]] = None):
        """Update post with rewritten content"""
        try:
            self.client.table('posts').update({
                'rewritten_title': rewritten_title,
                'rewritten_content': rewritten_content,
                'meta_description': meta_description,
                'suggested_tags': suggested_tags or [],
                'status': 'rewritten',
                'updated_at': datetime.now().isoformat()
            }).eq('id', post_id).execute()
        except Exception as e:
            print(f"Error updating rewritten post: {str(e)}")
            raise

    def update_post_scheduled(self, post_id: str, scheduled_time: datetime):
        """Update post with scheduled time"""
        try:
            self.client.table('posts').update({
                'scheduled_time': scheduled_time.isoformat(),
                'status': 'scheduled',
                'updated_at': datetime.now().isoformat()
            }).eq('id', post_id).execute()
        except Exception as e:
            print(f"Error updating scheduled post: {str(e)}")

    def update_post_published(self, post_id: str, published_url: str):
        """Update post as published"""
        try:
            self.client.table('posts').update({
                'published_url': published_url,
                'status': 'published',
                'updated_at': datetime.now().isoformat()
            }).eq('id', post_id).execute()
        except Exception as e:
            print(f"Error updating published post: {str(e)}")
            raise

    def update_post_failed(self, post_id: str, error_message: str):
        """Mark post as failed"""
        try:
            self.client.table('posts').update({
                'status': 'failed',
                'meta_description': error_message,
                'updated_at': datetime.now().isoformat()
            }).eq('id', post_id).execute()
        except Exception as e:
            print(f"Error marking post as failed: {str(e)}")

    def get_statistics(self) -> Dict[str, int]:
        """Get migration statistics"""
        try:
            sources_count = len(self.client.table('sources').select('id', count='exact').execute().data)

            extracted_count = len(
                self.client.table('posts').select('id', count='exact')
                .eq('status', 'extracted').execute().data
            )

            published_count = len(
                self.client.table('posts').select('id', count='exact')
                .eq('status', 'published').execute().data
            )

            pending_count = len(
                self.client.table('posts').select('id', count='exact')
                .in_('status', ['extracted', 'rewritten', 'scheduled']).execute().data
            )

            return {
                'total_sources': sources_count,
                'total_extracted': extracted_count,
                'total_published': published_count,
                'total_pending': pending_count
            }
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {
                'total_sources': 0,
                'total_extracted': 0,
                'total_published': 0,
                'total_pending': 0
            }

    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts with source information"""
        try:
            response = self.client.table('posts')\
                .select('*, sources(name)')\
                .order('updated_at', desc=True)\
                .limit(limit)\
                .execute()

            posts = []
            for post in response.data:
                post_data = dict(post)
                if 'sources' in post_data and post_data['sources']:
                    post_data['source_name'] = post_data['sources']['name']
                else:
                    post_data['source_name'] = 'Unknown'
                posts.append(post_data)

            return posts
        except Exception as e:
            print(f"Error getting recent posts: {str(e)}")
            return []

    def get_source_post_count(self, source_id: str) -> int:
        """Get post count for a source"""
        try:
            response = self.client.table('posts')\
                .select('id', count='exact')\
                .eq('source_id', source_id)\
                .execute()

            return len(response.data)
        except Exception as e:
            print(f"Error getting source post count: {str(e)}")
            return 0

    def clear_all_data(self):
        """Clear all migration data"""
        try:
            self.client.table('posts').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            self.client.table('sources').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        except Exception as e:
            print(f"Error clearing data: {str(e)}")

    def add_blogger_config(self, blog_name: str, publish_method: str,
                          blog_id: Optional[str] = None, api_key: Optional[str] = None,
                          email_address: Optional[str] = None,
                          smtp_server: str = 'smtp.gmail.com', smtp_port: int = 587,
                          smtp_username: Optional[str] = None,
                          smtp_password: Optional[str] = None,
                          is_default: bool = False) -> bool:
        """Add Blogger configuration"""
        try:
            if is_default:
                self.client.table('blogger_configs').update({
                    'is_default': False
                }).eq('is_default', True).execute()

            self.client.table('blogger_configs').insert({
                'blog_name': blog_name,
                'publish_method': publish_method,
                'blog_id': blog_id,
                'api_key': api_key,
                'email_address': email_address,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'smtp_username': smtp_username,
                'smtp_password': smtp_password,
                'is_default': is_default
            }).execute()
            return True
        except Exception as e:
            print(f"Error adding blogger config: {str(e)}")
            return False

    def get_all_blogger_configs(self) -> List[Dict[str, Any]]:
        """Get all Blogger configurations"""
        try:
            response = self.client.table('blogger_configs').select('*').order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting blogger configs: {str(e)}")
            return []

    def get_default_blogger_config(self) -> Optional[Dict[str, Any]]:
        """Get default Blogger configuration"""
        try:
            response = self.client.table('blogger_configs').select('*').eq('is_default', True).maybeSingle().execute()
            return response.data
        except Exception as e:
            print(f"Error getting default blogger config: {str(e)}")
            return None

    def get_blogger_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get specific Blogger configuration"""
        try:
            response = self.client.table('blogger_configs').select('*').eq('id', config_id).maybeSingle().execute()
            return response.data
        except Exception as e:
            print(f"Error getting blogger config: {str(e)}")
            return None

    def update_blogger_config(self, config_id: str, **kwargs) -> bool:
        """Update Blogger configuration"""
        try:
            if kwargs.get('is_default'):
                self.client.table('blogger_configs').update({
                    'is_default': False
                }).eq('is_default', True).execute()

            self.client.table('blogger_configs').update(kwargs).eq('id', config_id).execute()
            return True
        except Exception as e:
            print(f"Error updating blogger config: {str(e)}")
            return False

    def delete_blogger_config(self, config_id: str) -> bool:
        """Delete Blogger configuration"""
        try:
            self.client.table('blogger_configs').delete().eq('id', config_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting blogger config: {str(e)}")
            return False
