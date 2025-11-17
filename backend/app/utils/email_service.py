# Email service using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
from core.config import get_settings

settings = get_settings()


class EmailService:
    def __init__(self):
        """Initialize SendGrid client with API key from environment variables"""
        self.api_key = settings.SENDGRID_API_KEY
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is not set")
        
        self.client = SendGridAPIClient(self.api_key)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = 'creditbusters2025@gmail.com',
        plain_text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email address
            plain_text_content: Optional plain text version of the email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add plain text content if provided
            if plain_text_content:
                message.plain_text_content = plain_text_content
            
            response = self.client.send(message)
            
            # SendGrid returns 202 for successful email acceptance
            if response.status_code == 202:
                print(f"Email sent successfully to {to_email}")
                return True
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                print(f"Response body: {response.body}")
                return False
                
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'body'):
                print(f"Error body: {e.body}")
            if hasattr(e, 'headers'):
                print(f"Error headers: {e.headers}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_code: str) -> bool:
        """
        Send a password reset email with the recovery code
        
        Args:
            to_email: Email address to send the reset code to
            reset_code: The password reset code
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "Código de Recuperación de Contraseña - Credit Busters"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Recuperación de Contraseña</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Credit Busters</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0;">Recuperación de Contraseña</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #ddd;">
                <h2 style="color: #333; margin-top: 0;">¡Hola!</h2>
                
                <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en Credit Busters.</p>
                
                <div style="background: #fff; border: 2px solid #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Tu código de recuperación es:</p>
                    <h1 style="margin: 10px 0; font-size: 32px; color: #667eea; letter-spacing: 5px; font-family: 'Courier New', monospace;">{reset_code}</h1>
                    <p style="margin: 0; font-size: 12px; color: #999;">Este código expira en 15 minutos</p>
                </div>
                
                <p><strong>Para restablecer tu contraseña:</strong></p>
                <ol style="padding-left: 20px;">
                    <li>Regresa a la aplicación de Credit Busters</li>
                    <li>Ingresa este código en el campo correspondiente</li>
                    <li>Establece tu nueva contraseña</li>
                </ol>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>⚠️ Importante:</strong> Si no solicitaste este restablecimiento, puedes ignorar este email. Tu contraseña no será cambiada.</p>
                </div>
                
                <p style="margin-top: 30px; color: #666;">
                    Saludos,<br>
                    <strong>El equipo de Credit Busters</strong>
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding: 15px; font-size: 12px; color: #999;">
                <p>Este es un email automático, por favor no respondas a este mensaje.</p>
            </div>
        </body>
        </html>
        """
        
        plain_text_content = f"""
        Credit Busters - Recuperación de Contraseña
        
        ¡Hola!
        
        Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en Credit Busters.
        
        Tu código de recuperación es: {reset_code}
        
        Este código expira en 15 minutos.
        
        Para restablecer tu contraseña:
        1. Regresa a la aplicación de Credit Busters
        2. Ingresa este código en el campo correspondiente
        3. Establece tu nueva contraseña
        
        ⚠️ Importante: Si no solicitaste este restablecimiento, puedes ignorar este email. Tu contraseña no será cambiada.
        
        Saludos,
        El equipo de Credit Busters
        
        ---
        Este es un email automático, por favor no respondas a este mensaje.
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text_content
        )


# instance of the email service to be used throughout the application
email_service = EmailService()