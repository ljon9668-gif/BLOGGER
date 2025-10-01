from typing import List, Optional, Dict, Any
from blogger_publisher import BloggerPublisher
from email_publisher import EmailPublisher

class UnifiedPublisher:
    """Unified publisher that supports both API and email methods"""

    def __init__(self):
        self.api_publisher = None
        self.email_publisher = None

    def configure_api(self, api_key: str):
        """Configure API publisher"""
        self.api_publisher = BloggerPublisher(api_key)

    def configure_email(self, smtp_server: str, smtp_port: int,
                       smtp_username: str, smtp_password: str):
        """Configure email publisher"""
        self.email_publisher = EmailPublisher(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password
        )

    def publish_post(self, config: Dict[str, Any], title: str, content: str,
                    labels: Optional[List[str]] = None,
                    images: Optional[List[str]] = None) -> str:
        """
        Publish post using the configuration method

        Args:
            config: Blogger configuration dictionary with publish_method
            title: Post title
            content: Post content
            labels: Optional list of tags/labels
            images: Optional list of image URLs

        Returns:
            Published post URL or success message
        """

        publish_method = config.get('publish_method', 'api')

        if publish_method == 'api':
            return self._publish_via_api(config, title, content, labels)
        elif publish_method == 'email':
            return self._publish_via_email(config, title, content, labels, images)
        else:
            raise ValueError(f"Unknown publish method: {publish_method}")

    def _publish_via_api(self, config: Dict[str, Any], title: str,
                        content: str, labels: Optional[List[str]]) -> str:
        """Publish via Blogger API"""

        blog_id = config.get('blog_id')
        api_key = config.get('api_key')

        if not blog_id:
            raise ValueError("Blog ID is required for API publishing")
        if not api_key:
            raise ValueError("API key is required for API publishing")

        if not self.api_publisher:
            self.configure_api(api_key)

        published_url = self.api_publisher.publish_post(
            blog_id=blog_id,
            title=title,
            content=content,
            labels=labels or []
        )

        return published_url

    def _publish_via_email(self, config: Dict[str, Any], title: str,
                          content: str, labels: Optional[List[str]],
                          images: Optional[List[str]]) -> str:
        """Publish via Blogger email"""

        email_address = config.get('email_address')
        smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = config.get('smtp_port', 587)
        smtp_username = config.get('smtp_username')
        smtp_password = config.get('smtp_password')

        if not email_address:
            raise ValueError("Blogger email address is required for email publishing")
        if not smtp_username or not smtp_password:
            raise ValueError("SMTP credentials are required for email publishing")

        if not EmailPublisher.validate_blogger_email(email_address):
            raise ValueError(f"Invalid Blogger email address: {email_address}")

        if not self.email_publisher or self.email_publisher.smtp_username != smtp_username:
            self.configure_email(smtp_server, smtp_port, smtp_username, smtp_password)

        success = self.email_publisher.publish_post(
            blogger_email=email_address,
            title=title,
            content=content,
            labels=labels,
            images=images
        )

        if success:
            return f"Email sent to {email_address}. Post will appear on your blog shortly."
        else:
            raise Exception("Failed to send email to Blogger")

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate Blogger configuration

        Returns:
            (is_valid, error_message)
        """

        publish_method = config.get('publish_method')

        if not publish_method:
            return False, "Publish method is required"

        if publish_method not in ['api', 'email']:
            return False, f"Invalid publish method: {publish_method}"

        if publish_method == 'api':
            if not config.get('blog_id'):
                return False, "Blog ID is required for API publishing"
            if not config.get('api_key'):
                return False, "API key is required for API publishing"

        elif publish_method == 'email':
            email = config.get('email_address')
            if not email:
                return False, "Blogger email address is required for email publishing"
            if not EmailPublisher.validate_blogger_email(email):
                return False, f"Invalid Blogger email format: {email}"
            if not config.get('smtp_username'):
                return False, "SMTP username is required for email publishing"
            if not config.get('smtp_password'):
                return False, "SMTP password is required for email publishing"

        return True, ""

    @staticmethod
    def get_required_fields(publish_method: str) -> List[str]:
        """Get required fields for a publish method"""

        if publish_method == 'api':
            return ['blog_name', 'blog_id', 'api_key']
        elif publish_method == 'email':
            return ['blog_name', 'email_address', 'smtp_username', 'smtp_password']
        else:
            return []
