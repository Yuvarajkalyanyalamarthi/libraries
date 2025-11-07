from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ---------- DATABASE CONFIG -----------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ---------- TABLE / MODEL -----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# ---------- REGISTER PAGE (STORE DATA IN DB) ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    page = """
        <h2>Register (Insert into Database)</h2>
        <form method="POST">
            <label>Username:</label>
            <input type="text" name="username" required><br><br>

            <label>Password:</label>
            <input type="password" name="password" required><br><br>

            <button type="submit">Register</button>
        </form>
        <br>
        <a href="/">Go to Login</a>
    """

    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        # INSERT INTO DATABASE
        new_user = User(username=user, password=pwd)
        db.session.add(new_user)
        db.session.commit()

        return "<h2>✅ Registration Successful! Data stored in DB.</h2><a href='/'>Go to Login</a>"

    return page



# ---------- LOGIN PAGE (CHECK FROM DB) ----------
@app.route("/", methods=["GET", "POST"])
def login():
    page = """
        <h2>Login (Fetch from Database)</h2>
        <form method="POST">
            <label>Username:</label>
            <input type="text" name="username" required><br><br>

            <label>Password:</label>
            <input type="password" name="password" required><br><br>

            <button type="submit">Login</button>
        </form>
        <br>
        <a href="/register">Create Account</a>
    """

    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        # DATABASE SELECT QUERY
        check_user = User.query.filter_by(username=user, password=pwd).first()

        if check_user:
            return "<h2>✅ Login Successful</h2>"
        else:
            return "<h2>❌ Invalid Credentials</h2>"

    return page



# ---------- RUN APP -----------
if __name__ == "__main__":
    with app.app_context():     # Required for create_all()
        db.create_all()         # Creates DB + Table automatically
    app.run(debug=True)
