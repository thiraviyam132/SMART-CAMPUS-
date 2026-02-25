from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Issue

app = Flask(__name__)

# ---------- CONFIG ----------
app.config['SECRET_KEY'] = 'smartcampus_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def build_ai_issue_help(issue_text):
    text = issue_text.lower()

    category_rules = [
        ("Fees", ["fee", "fees", "payment", "scholarship", "refund"]),
        ("Attendance", ["attendance", "absent", "present", "leave", "biometric"]),
        ("Library", ["library", "book", "journal", "borrow", "return"]),
        ("Exam Issue", ["exam", "mark", "result", "grade", "hall ticket"]),
    ]

    suggested_category = "Other"
    for category, words in category_rules:
        if any(word in text for word in words):
            suggested_category = category
            break

    high_priority_words = ["urgent", "immediately", "asap", "critical", "emergency"]
    medium_priority_words = ["soon", "delay", "important", "problem", "issue"]

    if any(word in text for word in high_priority_words):
        priority = "High"
    elif any(word in text for word in medium_priority_words):
        priority = "Medium"
    else:
        priority = "Normal"

    short_summary = issue_text.strip()
    if len(short_summary) > 140:
        short_summary = short_summary[:137].rstrip() + "..."

    action_items = [
        "Use a clear title with place, time, and affected department.",
        "Add one specific example so admin can verify quickly.",
        "Mention any previous complaint/ticket number if available.",
    ]

    return {
        "summary": short_summary,
        "suggested_category": suggested_category,
        "priority": priority,
        "recommended_next_steps": action_items,
        "suggested_title": f"{suggested_category}: {short_summary[:50].strip()}",
    }

# ---------- CREATE DEFAULT ADMIN ----------
def create_admin():
    admin_email = "admin@gmail.com"
    admin_password = "admin123"

    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            name="Admin",
            email=admin_email,
            password=generate_password_hash(admin_password),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    else:
        print("ℹ️ Admin already exists")

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'student':
                session['show_student_welcome'] = True
            return redirect(url_for('dashboard'))

        flash('Invalid email or password')

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if user.role == 'admin':
        issues = Issue.query.all()
        return render_template('admin_dashboard.html', user=user, issues=issues)

    issues = Issue.query.filter_by(user_id=user.id).all()
    show_student_welcome = session.pop('show_student_welcome', False)
    return render_template(
        'user_dashboard.html',
        user=user,
        issues=issues,
        show_student_welcome=show_student_welcome
    )


@app.route('/student_ai_helper', methods=['POST'])
def student_ai_helper():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(session['user_id'])
    if not user or user.role != 'student':
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    issue_text = (data.get('issue_text') or "").strip()

    if not issue_text:
        return jsonify({"error": "Please enter your issue details."}), 400

    ai_response = build_ai_issue_help(issue_text)
    return jsonify(ai_response)

# ---------- ADD ISSUE ----------
@app.route('/add_issue', methods=['GET', 'POST'])
def add_issue():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        issue = Issue(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            user_id=session['user_id']
        )
        db.session.add(issue)
        db.session.commit()

        flash('Issue added successfully')
        return redirect(url_for('dashboard'))

    return render_template('add_issue.html')

# ---------- UPDATE ISSUE STATUS (ADMIN ONLY) ----------
@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    issue = Issue.query.get_or_404(id)
    issue.status = request.form['status']
    db.session.commit()

    flash('Issue status updated')
    return redirect(url_for('dashboard'))

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- RUN ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()   # 👈 ADMIN AUTO CREATE
    app.run(debug=True)
