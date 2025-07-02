from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config
from jose import jwt
from datetime import datetime, timedelta

def allowed_file(filename: str) -> bool:
    allowed_extensions = {'pptx', 'docx', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_verification_email(email: str, token: str):
    message = Mail(
        from_email='inceptioncoderclub@gmail.com',
        to_emails=email,
        subject='Verify Your Email',
        html_content=f'Click to verify: http://localhost:8000/verify-email/{token}'
    )
    try:
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_secure_url(assignment_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"id": assignment_id, "exp": expire}, Config.SECRET_KEY, algorithm="HS256")

def decode_secure_url(token: str) -> int:
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload.get("id")
    except jwt.JWTError:
        return None