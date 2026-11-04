import sys
from app import create_app, db
from app.models import User

email, role = sys.argv[1].lower(), sys.argv[2]
if role not in ("customer", "officer", "admin"):
    sys.exit("Role must be customer, officer or admin")

app = create_app()
with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        sys.exit("No user with that email")
    user.role = role
    db.session.commit()
    print(user.email, "is now", user.role)