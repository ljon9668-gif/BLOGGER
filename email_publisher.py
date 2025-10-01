import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import List, Optional, Dict, Any
import requests
from io import BytesIO

class EmailPublisher:
    def __init__(self, smtp_server: str, smtp_port: int,
                 smtp_username: str, smtp_password: str):
        """Initialize email publisher for Blogger"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def publish_post(self, blogger_email: str, title: str, content: str,
                    labels: Optional[List[str]] = None,
                    images: Optional[List[str]] = None) -> bool:
        """
        Publish post to Blogger via email

        Email format:
        - Subject: Post title
        - Body: Post content (HTML or plain text)
        - Attachments: Images (will be embedded in post)
        """

        try:
            msg = MIMEMultipart('related')
            msg['From'] = self.smtp_username
            msg['To'] = blogger_email
            msg['Subject'] = title

            html_content = self._format_content_as_html(content, labels)

            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)

            msg_text = MIMEText(content, 'plain', 'utf-8')
            msg_alternative.attach(msg_text)

            msg_html = MIMEText(html_content, 'html', 'utf-8')
            msg_alternative.attach(msg_html)

            if images:
                for idx, image_url in enumerate(images[:5]):
                    try:
                        img_data = self._download_image(image_url)
                        if img_data:
                            image = MIMEImage(img_data)
                            image.add_header('Content-ID', f'<image{idx}>')
                            image.add_header('Content-Disposition', 'inline',
                                           filename=f'image{idx}.jpg')
                            msg.attach(image)
                    except Exception as e:
                        print(f"Warning: Could not attach image {image_url}: {str(e)}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            raise Exception(f"Failed to send email to Blogger: {str(e)}")

    def _format_content_as_html(self, content: str, labels: Optional[List[str]] = None) -> str:
        """Format content as HTML for email"""

        paragraphs = content.split('\n\n')
        html_content = '<div style="font-family: Arial, sans-serif; line-height: 1.6;">\n'

        for para in paragraphs:
            if para.strip():
                para_html = para.strip()

                para_html = para_html.replace('**', '<strong>').replace('**', '</strong>')
                para_html = para_html.replace('*', '<em>').replace('*', '</em>')

                if para.strip().startswith('- ') or para.strip().startswith('• '):
                    items = [item.strip('- •').strip() for item in para.split('\n')
                            if item.strip().startswith(('- ', '• '))]
                    html_content += '<ul>\n'
                    for item in items:
                        html_content += f'  <li>{item}</li>\n'
                    html_content += '</ul>\n'
                elif para.strip().startswith(('1. ', '2. ', '3. ')):
                    items = []
                    for line in para.split('\n'):
                        line = line.strip()
                        if line and line[0].isdigit() and '. ' in line:
                            items.append(line.split('. ', 1)[1])
                    html_content += '<ol>\n'
                    for item in items:
                        html_content += f'  <li>{item}</li>\n'
                    html_content += '</ol>\n'
                else:
                    html_content += f'<p>{para_html}</p>\n'

        if labels:
            html_content += '<div style="margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">\n'
            html_content += '<p style="margin: 0; font-size: 14px; color: #666;"><strong>Tags:</strong> '
            html_content += ', '.join(labels)
            html_content += '</p>\n</div>\n'

        html_content += '</div>'

        return html_content

    def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading image {url}: {str(e)}")
            return None

    @staticmethod
    def validate_blogger_email(email: str) -> bool:
        """Validate Blogger email format"""
        if not email or '@blogger.com' not in email.lower():
            return False

        parts = email.split('@')
        if len(parts) != 2:
            return False

        username = parts[0]
        if '.' not in username:
            return False

        return True

    @staticmethod
    def get_blogger_email_help() -> str:
        """Get help text for Blogger email setup"""
        return """
Como configurar publicação via email no Blogger:

1. Acesse seu blog no Blogger (blogger.com)
2. Vá em "Configurações" > "Email"
3. Na seção "Postar por e-mail", você verá um endereço de email único
4. O formato é: seu_email.chave_secreta@blogger.com

Exemplo: joaquimildefonso090.ildefonso090@blogger.com

Configuração SMTP:
- Use uma conta Gmail ou outro provedor SMTP
- Para Gmail, ative "Acesso de apps menos seguros" ou use "Senha de app"
- SMTP Server: smtp.gmail.com
- SMTP Port: 587

Formato do email:
- Assunto → Título da postagem
- Corpo → Conteúdo da postagem
- Anexos de imagem → Serão inseridos na postagem
"""
