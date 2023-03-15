from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError

from flask_mysqldb import MySQL
from models.ModelUser import ModelUser
from models.ModelProduct import ModelProduct as MP
from models.ModelDevice import ModelDevice as MD
from models.ModelItem import ModelItem as MI
# entities
from models.entities.User import User
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL configuration
app.config['MYSQL_HOST'] = 'database-1.cysbdhj0q37n.ap-southeast-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test123456'
app.config['MYSQL_DB'] = 'demo'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

db = MySQL(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return ModelUser.get_by_id(db, user_id)
# Example route that uses the database connection
@app.route('/')
def index():
    cur = db.connection.cursor()
    cur.execute('''SELECT * FROM devices''')
    results = cur.fetchall()
    cur.close()
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user is not None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password!!!')
                return redirect(url_for('login'))
        else:
            flash("User not found!!!")
            return render_template('login.html')
    else:
        return render_template('login.html')
if __name__ == '__main__':
    csrf.init_app(app)
    
    app.run()
