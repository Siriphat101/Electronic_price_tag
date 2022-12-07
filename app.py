from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, make_response
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import config

# models
from models.ModelUser import ModelUser
from models.ModelProduct import ModelProduct as MP
from models.ModelDevice import ModelDevice as MD

# entities
from models.entities.User import User
from models.entities.Product import Product
# from models.CRUD import CRUD
from models.entities.Device import Device

app = Flask(__name__)

csrf = CSRFProtect(app)
db = MySQL(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return ModelUser.get_by_id(db, user_id)


# config database
app.config['MYSQL_HOST'] = config['development'].MYSQL_HOST
app.config['MYSQL_USER'] = config['development'].MYSQL_USER
app.config['MYSQL_PASSWORD'] = config['development'].MYSQL_PASSWORD
app.config['MYSQL_DB'] = config['development'].MYSQL_DB

app.secret_key = config['development'].SECRET_KEY


# CRUD API


@app.route('/')
def home():  #

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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# if error 401, redirect to login page
@app.errorhandler(401)
def page_not_found(e):
    return render_template("login.html")


@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.fname, current_user.lname)

    return render_template('dashboard.html')


@app.route('/products')
@login_required
def products():
    products = MP.get_all(db)
    return render_template('products.html', products=products)




if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.run(debug=True)
