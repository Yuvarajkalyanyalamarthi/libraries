from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- NEW CONFIGURATION FOR SQL SERVER ---

# Your server and database details
SERVER_NAME = 'kalyan'
DATABASE_NAME = 'my_flask_app' # Make sure this database exists on your server!

# The connection string for Windows Authentication
# It specifies the driver and tells it to use a trusted connection
CONNECTION_STRING = (
    f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?"
    f"driver=ODBC+Driver+17+for+SQL+Server&"
    f"Trusted_Connection=yes"
)

app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# --- Your models and routes go here as before ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/')
def index():
    return "Welcome to the Flask App with SQL Server!"   

if __name__ == "__main__":
    app.run(debug=True)