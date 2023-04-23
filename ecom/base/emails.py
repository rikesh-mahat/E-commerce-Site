from django.conf import settings
from django.core.mail import send_mail

def send_account_activation_mail(email, email_token):
    subject = "Verify your account"
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi, click on the link to activate your account http://127.0.0.1:8000/accounts/activate/{email_token}'
    
    send_mail(subject,message, email_from, [email])
    
    
def send_forgotpassword_email(email, auth_code):
    subject = "Password Reset Request"
    email_from = settings.EMAIL_HOST_USER
    message = f"Your verification code for password reset is {auth_code}"
    
    send_mail(subject,message, email_from, [email])