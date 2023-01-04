# pythonanywhere mintball777888999::testpythondeploy777
from sqlite3 import IntegrityError
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
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/testpythondeploy777'
app.config['MYSQL_HOST'] = config['development'].MYSQL_HOST
app.config['MYSQL_USER'] = config['development'].MYSQL_USER
app.config['MYSQL_PASSWORD'] = config['development'].MYSQL_PASSWORD
app.config['MYSQL_DB'] = config['development'].MYSQL_DB

app.secret_key = config['development'].SECRET_KEY

        

# CRUD API


@app.route('/')
def home():  

    return render_template('index.html')

# success
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

# success
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# if error 401, redirect to login page
@app.errorhandler(401)
def page_not_found(e):
    return render_template("login.html")

# Global variables
count = [] 
@app.route('/dashboard')
@login_required
def dashboard():
    
    total_devices = MD.count_device(db)
    on_devices = MD.statusON_device(db)
    off_devices = MD.statusOFF_device(db)
    error_devices = total_devices - (on_devices + off_devices)
    count.append(total_devices)
    count.append(on_devices)
    count.append(off_devices)
    count.append(error_devices)
    
    
    
    

    return render_template('dashboard.html', count=count)

# success
@app.route('/products')
@login_required
def products():
    products = MP.get_all_products(db)   
    return render_template('product.html', products=products)

# success
@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            
            cur = db.connection.cursor()
            
            #  check product_id and product_price is number
            if product_id.isnumeric() and product_price.isnumeric():
                
                
                # cur.execute("SELECT product_id FROM products ")
                # check_id_duplicate = cur.fetchall()
                # print(check_id_duplicate)
                
                
                cur.execute("INSERT INTO products (product_id, product_name, product_price) VALUES (%s, %s,%s)", (product_id, product_name, product_price))
                db.connection.commit()
                # print("Product added successfully")
                flash("success add product")
                return redirect(url_for('product'))
               
            else:
                flash("id and price must be number")
                # print("Product id and price must be number")
            
        
        except Exception as e:
            flash("id is duplicate")
            raise e
            
        finally:
            return redirect(url_for('products'))

# success
@app.route('/update_product/<id>', methods=['POST'])
@login_required
def update_product(id):
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            product_name = request.form['product_name']
            product_price = request.form['product_price']
            
            cur = db.connection.cursor()
            
            # check product_id and product_price is number
            if product_id.isnumeric() and product_price.isnumeric():   
                    
                sql = "UPDATE products SET product_id = %s, product_name = %s, product_price = %s WHERE id = %s"
                val = (product_id, product_name, product_price, id)
                
                cur.execute(sql, val)
            
                db.connection.commit()
                flash("success update")
                return redirect(url_for('products'))
      
            else:
                flash("id and price must be number")
        except Exception as e:
            # trow trow trow
            flash("id is duplicate")
            raise e
        
        finally:
            # do do do
            return redirect(url_for('products'))
  
# success
@app.route('/delete_product/<id>', methods=['GET'])
@login_required
def delete_product(id):
    
    cur = db.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s",(id,))
    db.connection.commit()
    return redirect(url_for('products'))


@app.route('/devices')
def devices():
    devices = MD.get_all_devices(db)
    return render_template('device.html', devices=devices)


# no
@app.route('/add_device', methods=['POST'])
@login_required
def add_device():
    if request.method == 'POST':
        try:
            chipID = request.form['chipID']
            name = request.form['device_name']
            
            
            cur = db.connection.cursor()
                     
            if chipID.isnumeric():
                cur.execute("SELECT chipID FROM devices ")
                check_id_duplicate = cur.fetchall()
                print(check_id_duplicate)
                print(chipID)
                
                # check chipID is not duplicate 
                    
                if chipID != check_id_duplicate:
                
                    cur.execute("INSERT INTO devices (chipID, name, status) VALUES (%s, %s,%s)", (chipID, name, 0))
                    db.connection.commit()
                    
                    flash("success add device")
                    return redirect(url_for('devices'))
                else:
                    flash("id is duplicate")
            
        
        except Exception as e:
            raise e

        finally:
            return redirect(url_for('devices'))
 

@app.route('/update_device/<id>', methods=['POST'])
@login_required
def update_device(id):
    if request.method == 'POST':
        try:
            device_id = request.form['chipID']
            device_name = request.form['device_name']
            

            # check product_id and product_price is number
            if device_id.isnumeric():
                cur = db.connection.cursor()
                cur.execute("SELECT product_id FROM products ")
                check_id_duplicate = cur.fetchall()
                
                # check product_id is not duplicate
                if device_id is not check_id_duplicate:
                    
                    sql = "UPDATE products SET chipID = %s, name = %s WHERE id = %s"
                    val = (device_id, device_name, id)
                    
                    cur.execute(sql, val)
                
                    db.connection.commit()
                    flash("success update")
                    return redirect(url_for('devices'))
                else:
                    flash("id is duplicate")
                    
            
        except Exception as e:
            raise e
        
        finally:
            return redirect(url_for('devices'))

@app.route('/delete_device/<id>', methods=['GET'])
@login_required
def delete_device(id):
    
    cur = db.connection.cursor()
    cur.execute("DELETE FROM devices WHERE id = %s",(id,))
    db.connection.commit()
    return redirect(url_for('devices'))


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.run()
