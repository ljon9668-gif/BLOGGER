import feedparser
import trafilatura
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

class ContentExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_from_url(self, url: str, max_posts: int = 10) -> List[Dict[str, Any]]:
        """Extract content from URL (RSS or webpage)"""
        # Try RSS feed first
        posts = self._extract_from_rss(url, max_posts)
        
        if not posts:
            # Try web scraping
            posts = self._extract_from_webpage(url, max_posts)
        
        return posts
    
    def _extract_from_rss(self, url: str, max_posts: int) -> List[Dict[str, Any]]:
        """Extract posts from RSS feed"""
        try:
            feed = feedparser.parse(url)
            
            if not feed.entries:
                return []
            
            posts = []
            for entry in feed.entries[:max_posts]:
                post = {
                    'title': entry.get('title', 'Untitled'),
                    'url': entry.get('link', url),
                    'content': '',
                    'images': [],
                    'tags': []
                }
                
                # Extract content
                if 'content' in entry:
                    post['content'] = entry.content[0].get('value', '')
                elif 'summary' in entry:
                    post['content'] = entry.get('summary', '')
                elif 'description' in entry:
                    post['content'] = entry.get('description', '')
                
                # Clean HTML from content
                post['content'] = self._clean_html(post['content'])
                
                # Extract tags
                if 'tags' in entry:
                    post['tags'] = [tag.term for tag in entry.tags]
                
                # Extract images from content
                post['images'] = self._extract_images_from_html(entry.get('summary', '') + post['content'])
                
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"RSS extraction error: {str(e)}")
            return []
    
    def _extract_from_webpage(self, url: str, max_posts: int) -> List[Dict[str, Any]]:
        """Extract posts from webpage using web scraping"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Use trafilatura to extract main content
            downloaded = trafilatura.fetch_url(url)
            main_content = trafilatura.extract(downloaded)
            
            if not main_content:
                return []
            
            # Try to find article links on the page
            soup = BeautifulSoup(response.text, 'html.parser')
            article_links = self._find_article_links(soup, url)
            
            posts = []
            
            # If we found article links, scrape each one
            if article_links:
                for link in article_links[:max_posts]:
                    post = self._scrape_single_article(link)
                    if post:
                        posts.append(post)
            else:
                # Otherwise, treat the whole page as one post
                post = {
                    'title': self._extract_title(soup),
                    'url': url,
                    'content': main_content,
                    'images': self._extract_images_from_html(response.text),
                    'tags': []
                }
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Webpage extraction error: {str(e)}")
            return []
    
    def _scrape_single_article(self, url: str) -> Dict[str, Any]:
        """Scrape a single article"""
        try:
            downloaded = trafilatura.fetch_url(url)
            content = trafilatura.extract(downloaded)
            
            if not content:
                return None
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'title': self._extract_title(soup),
                'url': url,
                'content': content,
                'images': self._extract_images_from_html(response.text),
                'tags': self._extract_meta_keywords(soup)
            }
            
        except Exception as e:
            print(f"Article scraping error for {url}: {str(e)}")
            return None
    
    def _find_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find article links on a page"""
        links = []
        
        # Common article link patterns
        article_selectors = [
            'article a[href]',
            '.post a[href]',
            '.entry a[href]',
            'h2 a[href]',
            'h3 a[href]',
            '.blog-post a[href]'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for elem in elements:
                href = elem.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self._is_valid_article_url(full_url, base_url):
                        links.append(full_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def _is_valid_article_url(self, url: str, base_url: str) -> bool:
        """Check if URL is likely an article"""
        # Must be from same domain
        if urlparse(url).netloc != urlparse(base_url).netloc:
            return False
        
        # Exclude common non-article patterns
        exclude_patterns = [
            r'/tag/', r'/category/', r'/author/', r'/page/',
            r'/search/', r'/feed/', r'/rss/', r'\#',
            r'/login', r'/register', r'/archive/'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML"""
        # Try multiple title locations
        title = None
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        
        # Try meta title
        if not title:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '').strip()
        
        # Try page title
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
        
        return title or 'Untitled Post'
    
    def _extract_images_from_html(self, html: str) -> List[str]:
        """Extract image URLs from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and src.startswith('http'):
                images.append(src)
        
        return images[:5]  # Limit to 5 images
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags"""
        keywords = []
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            content = meta_keywords.get('content', '')
            keywords = [k.strip() for k in content.split(',')]
        
        return keywords[:10]  # Limit to 10 keywords
    
    def _clean_html(self, html: str) -> str:
        """Clean HTML and extract text"""
        if not html:
            return ''
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'meta', 'link']):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=' ')
        
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
