from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
from datetime import datetime

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASS,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_digest_email(summary_text: str):
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        return
        
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        <h2>CodePulse Weekly</h2>
        <div style="background: #f9f9f9; padding: 20px; border-radius: 8px;">
            {summary_text.replace(chr(10), '<br>')}
        </div>
    </div>
    """
    
    message = MessageSchema(
        subject=f"CodePulse Weekly — Week of {datetime.now().strftime('%Y-%m-%d')}",
        recipients=[settings.DIGEST_EMAIL],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"Error sending email: {e}")
