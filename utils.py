from urllib.parse import urlparse
import re

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def extract_domain(url: str) -> str:
    """Extract domain name from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return url

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ''
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.,!?;:\-\'\"()]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix

def format_date(date_str: str, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format date string"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(format)
    except Exception:
        return date_str

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters"""
    # Remove invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes"""
    if not text:
        return 0
    
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    
    return max(1, round(minutes))

def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """Extract potential keywords from text (simple implementation)"""
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = text.lower().split()
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Filter words
    filtered_words = [
        word for word in words 
        if word not in stop_words and len(word) > 3
    ]
    
    # Count frequency
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_keywords[:max_keywords]]

def is_valid_blog_id(blog_id: str) -> bool:
    """Validate Blogger blog ID format"""
    # Blogger IDs are typically numeric strings
    return bool(re.match(r'^\d+$', blog_id))

def format_labels_for_blogger(tags: list) -> list:
    """Format tags for Blogger API (max 20, no special chars)"""
    if not tags:
        return []
    
    formatted = []
    for tag in tags[:20]:  # Blogger limit
        # Remove special characters, keep only alphanumeric and spaces
        clean_tag = re.sub(r'[^a-zA-Z0-9\s]', '', str(tag))
        clean_tag = clean_tag.strip()
        
        if clean_tag:
            formatted.append(clean_tag)
    
    return formatted
