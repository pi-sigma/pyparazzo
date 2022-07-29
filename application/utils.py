import os
import smtplib

import bleach
from email.message import EmailMessage
from flask import redirect, request, url_for, flash
from flask_login import current_user
from functools import wraps


# Email
MY_EMAIL = os.environ.get("MY_EMAIL")
GMAIL_PWD = os.environ.get("GMAIL_PWD")


# Helper function to sanitize input
def sanitize_html(content):
    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br', 'div', 'dl', 'dt',
                    'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small', 'strike',
                    'span', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
                    'thead', 'tr', 'tt', 'u', 'ul']
    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
    }
    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)
    return cleaned


# decorator for restricting access to admin
# decorators: https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/#login-required-decorator
def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("main_bp.login", next=request.url))
        elif current_user.id != 1:
            flash("Only admin can create/edit posts", "error")
            return redirect(url_for("main_bp.index"))
        else:
            return function(*args, **kwargs)
    return wrapper


def send_mail(subject, sender, content):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = MY_EMAIL
    msg.set_content(content)

    with smtplib.SMTP("smtp.gmail.com", port=587) as server:
        server.starttls()
        server.login(user=MY_EMAIL, password=GMAIL_PWD)
        server.send_message(msg)
