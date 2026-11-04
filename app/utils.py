from functools import wraps
from flask import abort
from flask_login import current_user

def calculate_monthly_payment(amount,annual_rate,months):
   r = annual_rate / 100 / 12
   if r == 0:
       return amount / months
   return amount * r / (1 - (1 + r) ** -months)


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator