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

def build_schedule(amount, annual_rate, months):
    r = annual_rate / 100 / 12
    payment = calculate_monthly_payment(amount, annual_rate, months)
    balance = amount
    rows = []
    for m in range(1, months + 1):
        interest = balance * r
        principal = payment - interest
        balance = max(balance - principal, 0)
        rows.append((m, payment, principal, interest, balance))
    return rows