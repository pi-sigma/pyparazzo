import bleach
from flask import redirect, request, url_for
from flask_login import current_user
from functools import wraps


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
def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return redirect(url_for("login", next=request.url))
        elif current_user.id == 1:
            return function(*args, **kwargs)
        else:
            return "Admin only"
    return wrapper


# Documentation
# decorators: https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/#login-required-decorator
