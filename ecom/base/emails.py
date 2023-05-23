from django.conf import settings
from django.core.mail import send_mail   
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random

def send_account_activation_mail(username, email, email_token):
    # subject = "Verify your account"
    # email_from = settings.EMAIL_HOST_USER
    # message = f'Hi, click on the link to activate your account http://127.0.0.1:8000/accounts/activate/{email_token}'
    
    # send_mail(subject,message, email_from, [email])
    

    subject = "Activate Your Account"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]

    # Load the email template and render it with the given context
    context = {'username': username, 'token': email_token}
    html_content = render_to_string('accounts/verification_link.html', context)
    text_content = strip_tags(html_content)

    # Create the email message object with both HTML and plain text content
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()
    


def send_verification_code(username, code, user_mail):
    subject = "Verification Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_mail]

    # Load the email template and render it with the given context
    context = {'username': username, 'code': code}
    html_content = render_to_string('accounts/verification_email.html', context)
    text_content = strip_tags(html_content)

    # Create the email message object with both HTML and plain text content
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

def send_invoice_email(username, order, user_email):
    subject = "Invoice"
    from_email = from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]
    
    
    cart = order.cart
    cart_items = cart.cart_items.all()
    
    context = {'username': username, 'items' : cart_items, 'order' : order}
    html_content = render_to_string('accounts/invoice.html', context)
    text_content = strip_tags(html_content)
    
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()
    
    

def send_congratulation_email(username, order, user_email):
    subject = "Your Item has been bought"
    from_email = from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]
    
    
    cart = order.cart
    cart_items = cart.cart_items.all()
    
    number = random.randint(00000, 999999)
    context = {'username': username, 'items' : cart_items, 'order' : order, 'number' : number}
    html_content = render_to_string('accounts/congratulation.html', context)
    text_content = strip_tags(html_content)
    
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()