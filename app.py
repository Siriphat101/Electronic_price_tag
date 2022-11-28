from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, make_response
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect,CSRFError
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
def Home():  #

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'])
        logged_user = ModelUser.login(db, user)
        if logged_user is not None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('Dashboard'))
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
    return redirect(url_for('Home'))


# if error 401, redirect to login page
@app.errorhandler(401)
def page_not_found(e):
    return redirect(url_for('login')), 401


@app.route('/dashboard')
@login_required
def Dashboard():
    print(current_user.fname, current_user.lname)

    # print all products
    # for p in MP.get_all_products(db):
    #     print(p.product_name)

    return render_template('dashboard.html')


@app.route('/product')
def Product():
    products = MP.get_all_products(db)
    # devices = MD.get_all_devices(db)

    # for i in products:
    #     print(i.product_name)
    # for i in devices:
    #     print(i.esp_name)
    #

    return render_template('product.html', products=products)


@app.route('/product/add', methods=['GET', 'POST'])
def AddProduct():

    if request.method == 'POST':
        product = Product(0, request.form['product_id'], request.form['product_name'], request.form['product_price'])
        print(product)
        # MP.add_product(db, product)
        return redirect(url_for('Product'))
    else:
        return redirect(url_for('Product'))





@app.route('/device')
def Device():
    devices = MD.get_all_devices(db)

    return render_template('device.html', devices=devices)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

@app.route('/setting')
def Setting():
    return render_template('setting.html')


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.run()
