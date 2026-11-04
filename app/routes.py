from flask import Blueprint, render_template, redirect, url_for, flash, request,current_app,abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms import RegistrationForm, LoginForm,LoanForm,PaymentForm   
from app.models import User,Loan,Payment  
from app.utils import calculate_monthly_payment,roles_required

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))                                                                      
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower(),
            phone=form.phone_number.data.strip()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/") and not next_page.startswith(("//","/\\")):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))
    return render_template("login.html", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@main.route("/dashboard")
@login_required
def dashboard():
    loans = (
        Loan.query.filter_by(user_id=current_user.id)
        .order_by(Loan.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", loans=loans)

@main.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    form = LoanForm()
    rate = current_app.config["INTEREST_RATE"]
    if form.validate_on_submit():
        monthly = calculate_monthly_payment(form.amount.data, rate, form.months.data)
        loan = Loan(
            user_id=current_user.id,
            amount=form.amount.data,
            months=form.months.data,
            interest_rate=rate,
            monthly_payment=monthly,
            purpose=(form.purpose.data or "").strip(),
        )
        db.session.add(loan)
        db.session.commit()
        flash("Application submitted. We will review it shortly.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("apply.html", form=form, rate=rate)

@main.route("/staff")
@login_required
@roles_required("officer", "admin")
def staff():
    status = request.args.get("status")
    query = Loan.query
    if status in ("Pending", "Approved", "Rejected","Paid"):
        query = query.filter_by(status=status)
    loans = query.order_by(Loan.created_at.desc()).all()
    return render_template("staff.html", loans=loans, status=status)


@main.route("/staff/loan/<int:loan_id>/<action>", methods=["POST"])
@login_required
@roles_required("officer", "admin")
def decide(loan_id, action):
    if action not in ("approve", "reject"):
        abort(400)
    loan = db.get_or_404(Loan, loan_id)
    if loan.status != "Pending":
        flash("That application was already decided.", "danger")
        return redirect(url_for("main.staff"))
    loan.status = "Approved" if action == "approve" else "Rejected"
    db.session.commit()
    flash(f"Loan #{loan.id} {loan.status.lower()}.", "success")
    return redirect(url_for("main.staff"))

@main.route("/staff/loan/<int:loan_id>", methods=["GET", "POST"])
@login_required
@roles_required("officer", "admin")
def loan_detail(loan_id):
    loan = db.get_or_404(Loan, loan_id)
    form = PaymentForm()
    if form.validate_on_submit():
        if loan.status != "Approved":
            flash("Payments can only be recorded on approved loans.", "danger")
        elif form.amount.data > loan.balance + 0.005:
            flash("That payment is more than the remaining balance.", "danger")
        else:
            db.session.add(Payment(
                loan_id=loan.id,
                amount=form.amount.data,
                recorded_by=current_user.id,
            ))
            db.session.commit()
            if loan.balance < 0.005:
                loan.status = "Paid"
                db.session.commit()
            flash("Payment recorded.", "success")
        return redirect(url_for("main.loan_detail", loan_id=loan.id))
    return render_template("staff_loan.html", loan=loan, form=form)