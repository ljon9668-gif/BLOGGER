import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
import json

class BloggerPublisher:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Blogger API client"""
        self.api_key = api_key or os.getenv("BLOGGER_API_KEY") or ""
        self.service = build('blogger', 'v3', developerKey=self.api_key)
    
    def publish_post(self, blog_id: str, title: str, content: str, 
                    labels: Optional[List[str]] = None, is_draft: bool = False) -> str:
        """Publish a post to Blogger"""
        
        try:
            # Prepare post body
            post_body: Dict[str, Any] = {
                'kind': 'blogger#post',
                'blog': {
                    'id': blog_id
                },
                'title': title,
                'content': content
            }
            
            # Add labels if provided
            if labels:
                post_body['labels'] = labels
            
            # Insert the post
            if is_draft:
                request = self.service.posts().insert(
                    blogId=blog_id,
                    body=post_body,
                    isDraft=True
                )
            else:
                request = self.service.posts().insert(
                    blogId=blog_id,
                    body=post_body
                )
            
            response = request.execute()
            
            # Return the published post URL
            return response.get('url', '')
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            raise Exception(f"Blogger API error: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to publish post: {str(e)}")
    
    def update_post(self, blog_id: str, post_id: str, title: str, 
                   content: str, labels: Optional[List[str]] = None) -> str:
        """Update an existing post"""
        
        try:
            post_body: Dict[str, Any] = {
                'kind': 'blogger#post',
                'id': post_id,
                'title': title,
                'content': content
            }
            
            if labels:
                post_body['labels'] = labels
            
            request = self.service.posts().update(
                blogId=blog_id,
                postId=post_id,
                body=post_body
            )
            
            response = request.execute()
            return response.get('url', '')
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            raise Exception(f"Blogger API error: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to update post: {str(e)}")
    
    def delete_post(self, blog_id: str, post_id: str) -> bool:
        """Delete a post"""
        
        try:
            request = self.service.posts().delete(
                blogId=blog_id,
                postId=post_id
            )
            request.execute()
            return True
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            raise Exception(f"Blogger API error: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to delete post: {str(e)}")
    
    def get_blog_info(self, blog_id: str) -> Dict[str, Any]:
        """Get blog information"""
        
        try:
            request = self.service.blogs().get(blogId=blog_id)
            response = request.execute()
            
            return {
                'id': response.get('id'),
                'name': response.get('name'),
                'description': response.get('description'),
                'url': response.get('url'),
                'posts_count': response.get('posts', {}).get('totalItems', 0)
            }
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            raise Exception(f"Blogger API error: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to get blog info: {str(e)}")
    
    def list_posts(self, blog_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """List posts from a blog"""
        
        try:
            request = self.service.posts().list(
                blogId=blog_id,
                maxResults=max_results
            )
            
            response = request.execute()
            posts = response.get('items', [])
            
            return [{
                'id': post.get('id'),
                'title': post.get('title'),
                'url': post.get('url'),
                'published': post.get('published'),
                'updated': post.get('updated'),
                'labels': post.get('labels', [])
            } for post in posts]
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            raise Exception(f"Blogger API error: {error_message}")
        except Exception as e:
            raise Exception(f"Failed to list posts: {str(e)}")
    
    def format_content_html(self, content: str, images: Optional[List[str]] = None) -> str:
        """Format content as HTML for Blogger"""
        
        # Convert paragraphs to HTML
        paragraphs = content.split('\n\n')
        html_content = ''
        
        for para in paragraphs:
            if para.strip():
                html_content += f'<p>{para.strip()}</p>\n'
        
        # Add images if provided
        if images:
            html_content += '<div class="post-images">\n'
            for img_url in images[:3]:  # Limit to 3 images
                html_content += f'<img src="{img_url}" alt="Post image" style="max-width: 100%; height: auto; margin: 10px 0;" />\n'
            html_content += '</div>\n'
        
        return html_content
