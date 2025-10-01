import os
from google import genai
from google.genai import types
from typing import Dict, List, Any

class AIRewriter:
    def __init__(self, api_key: str = None):
        """Initialize AI rewriter with Gemini API"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-exp"
    
    def rewrite_post(self, title: str, content: str, 
                    optimize_seo: bool = True,
                    improve_readability: bool = True,
                    generate_meta: bool = True,
                    suggest_tags: bool = True) -> Dict[str, Any]:
        """Rewrite a blog post with AI"""
        
        # Build the prompt based on options
        prompt = self._build_rewrite_prompt(
            title, content, optimize_seo, improve_readability, generate_meta, suggest_tags
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            result_text = response.text or ""
            
            # Parse the response
            result = self._parse_rewrite_response(result_text)
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to rewrite content: {str(e)}")
    
    def _build_rewrite_prompt(self, title: str, content: str,
                             optimize_seo: bool, improve_readability: bool,
                             generate_meta: bool, suggest_tags: bool) -> str:
        """Build prompt for content rewriting"""
        
        prompt = f"""You are an expert content writer and SEO specialist. Your task is to rewrite the following blog post to make it unique, engaging, and optimized.

**Original Title:** {title}

**Original Content:**
{content}

**Instructions:**
1. Rewrite the content completely to avoid plagiarism while preserving the core message and information
2. Make the content more engaging and natural-sounding
"""
        
        if optimize_seo:
            prompt += "3. Optimize for SEO with relevant keywords naturally incorporated\n"
        
        if improve_readability:
            prompt += "4. Improve readability with clear paragraphs, transitions, and structure\n"
        
        if generate_meta:
            prompt += "5. Generate a compelling meta description (150-160 characters)\n"
        
        if suggest_tags:
            prompt += "6. Suggest 5-8 relevant tags/keywords for the post\n"
        
        prompt += """
**Output Format:**
Please respond in the following format:

REWRITTEN_TITLE:
[Your rewritten title here]

REWRITTEN_CONTENT:
[Your complete rewritten content here - make it substantial and detailed]

META_DESCRIPTION:
[Meta description if requested]

TAGS:
[Comma-separated tags if requested]

Remember: The rewritten content should be completely original while maintaining the same information and value as the original.
"""
        
        return prompt
    
    def _parse_rewrite_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        
        result = {
            'title': '',
            'content': '',
            'meta_description': '',
            'tags': []
        }
        
        # Split response into sections
        sections = response_text.split('\n\n')
        current_section = None
        
        for section in sections:
            section = section.strip()
            
            if section.startswith('REWRITTEN_TITLE:'):
                current_section = 'title'
                result['title'] = section.replace('REWRITTEN_TITLE:', '').strip()
            
            elif section.startswith('REWRITTEN_CONTENT:'):
                current_section = 'content'
                result['content'] = section.replace('REWRITTEN_CONTENT:', '').strip()
            
            elif section.startswith('META_DESCRIPTION:'):
                current_section = 'meta'
                result['meta_description'] = section.replace('META_DESCRIPTION:', '').strip()
            
            elif section.startswith('TAGS:'):
                current_section = 'tags'
                tags_text = section.replace('TAGS:', '').strip()
                result['tags'] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            
            elif current_section and section:
                # Continue previous section
                if current_section == 'content':
                    result['content'] += '\n\n' + section
                elif current_section == 'meta':
                    result['meta_description'] += ' ' + section
        
        # Fallback if parsing failed
        if not result['title']:
            result['title'] = response_text.split('\n')[0][:100]
        
        if not result['content']:
            result['content'] = response_text
        
        return result
    
    def optimize_title_seo(self, title: str) -> str:
        """Optimize a title for SEO"""
        
        prompt = f"""Optimize this blog post title for SEO. Make it compelling, keyword-rich, and under 60 characters.

Original title: {title}

Provide only the optimized title, nothing else."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text.strip() if response.text else title
            
        except Exception as e:
            print(f"SEO optimization error: {str(e)}")
            return title
    
    def generate_meta_description(self, title: str, content: str) -> str:
        """Generate meta description from content"""
        
        # Limit content length for the prompt
        content_preview = content[:500] if len(content) > 500 else content
        
        prompt = f"""Generate a compelling meta description for this blog post. It should be 150-160 characters, engaging, and include key information.

Title: {title}

Content preview: {content_preview}

Provide only the meta description, nothing else."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            meta = response.text.strip() if response.text else ""
            
            # Ensure it's within character limit
            if len(meta) > 160:
                meta = meta[:157] + "..."
            
            return meta
            
        except Exception as e:
            print(f"Meta description generation error: {str(e)}")
            return ""
    
    def suggest_tags(self, title: str, content: str, max_tags: int = 8) -> List[str]:
        """Suggest relevant tags for a post"""
        
        content_preview = content[:500] if len(content) > 500 else content
        
        prompt = f"""Suggest {max_tags} relevant tags/keywords for this blog post. Tags should be concise (1-3 words each).

Title: {title}

Content: {content_preview}

Provide only the tags separated by commas, nothing else."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response.text:
                tags = [tag.strip() for tag in response.text.split(',')]
                return tags[:max_tags]
            
            return []
            
        except Exception as e:
            print(f"Tag suggestion error: {str(e)}")
            return []
