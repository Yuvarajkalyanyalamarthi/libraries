from flask import Flask
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

app = Flask(__name__)

SERVER_NAME = 'kalyan'
DATABASE_NAME = 'mywork' 

CONNECTION_STRING = (
    f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?"
    f"driver=ODBC+Driver+17+for+SQL+Server&"
    f"Trusted_Connection=yes"
)

app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def _repr_(self):
        return f'<User {self.username}>'

@app.route('/')
def index():
    return f"""
    <html>
        <head>
            <title>DB Connection Status</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                    text-align: center; 
                    margin-top: 100px; 
                }}
                h1 {{ color: #2c3e50; }}
                p {{ color: #34495e; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    background-color: #3498db;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }}
                .button:hover {{
                    background-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <h1>Connection Successful! ✅</h1>
            <p>Click the button below to see all tables in the '{escape(DATABASE_NAME)}' database.</p>
            <br>
            <a href="/tables" class="button">View Database Tables</a>
        </body>
    </html>
    """

@app.route('/tables')
def show_tables():
    try:
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        if not table_names:
            return f"Successfully connected, but no tables were found in '{DATABASE_NAME}'."
        
        html = f"""
        <html>
            <head>
                <title>Database Tables</title>
                <style>body {{ font-family: sans-serif; margin: 40px; }} li {{ margin-bottom: 10px; }}</style>
            </head>
            <body>
                <h1>Tables in '{escape(DATABASE_NAME)}'</h1>
                <ul>
        """
        for name in table_names:
            html += f"<li>{escape(name)} - <a href='/view/{escape(name)}'>View Top 5 Rows</a></li>"
        html += """
                </ul>
                <br>
                <a href="/">Back to Home</a>
            </body>
        </html>
        """
        return html

    except Exception as e:
        return f"An error occurred while inspecting the database: {str(e)}"

@app.route('/view/<string:table_name>')
def view_table(table_name):
    try:
        if not table_name.replace('_', '').isalnum():
             return "Invalid table name specified.", 400

        query = text(f"SELECT TOP 5 * FROM {table_name}")
        
        with db.engine.connect() as connection:
            result = connection.execute(query)
            rows = result.fetchall()
            columns = result.keys()

        if not rows:
            return f"Table '{escape(table_name)}' exists but is empty or no data was found."

        output_string = f"<h3>Showing Top 5 Rows from <i>{escape(table_name)}</i></h3>"
        output_string += ", ".join(columns) + "<br><br>"

        for row in rows:
            row_data = [str(item) for item in row]
            output_string += ", ".join(row_data) + "<br>"
        
        output_string += '<br><a href="/tables">Back to Table List</a>'

        return output_string

    except Exception as e:
        return f"An error occurred while querying table '{escape(table_name)}': {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)