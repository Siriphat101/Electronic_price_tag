# pythonanywhere mintball777888999::testpythondeploy777
from sqlite3 import IntegrityError
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import json
# MQTT library
import time
import paho.mqtt.client as paho
from paho import mqtt


from config import config

# models
from models.ModelUser import ModelUser
from models.ModelProduct import ModelProduct as MP
from models.ModelDevice import ModelDevice as MD
from models.ModelItem import ModelItem as MI


# entities
from models.entities.User import User
# from models.entities.Product import Product
# from models.CRUD import CRUD
# from models.entities.Device import Device

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


# MQTT setting
# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="jame", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("flaskweb", "123456789")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("c48a91514ddc4f8e8a4a69e6aa76c4b2.s2.eu.hivemq.cloud", 8883)

# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("price_tag1", qos=1)


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


@app.errorhandler(401)
def page_not_found(e):
    return render_template("login.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("home.html")



@app.route('/dashboard')
@login_required
def dashboard():

    count = []

    ItemData = MI.getItem(db)

    total_devices = MD.count_device(db)
    on_devices = MD.statusON_device(db)
    off_devices = MD.statusOFF_device(db)
    error_devices = total_devices - (on_devices + off_devices)
    count.append(total_devices)
    count.append(on_devices)
    count.append(off_devices)
    count.append(error_devices)

    return render_template('dashboard.html', count=count, ItemData=ItemData)

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
            
            data_json = {
            "target": "single",
            "node_id": product_id,
            "data": [
                product_name,
                product_price
            ]
            }

            json_data = json.dumps(data_json)

            cur = db.connection.cursor()

            #  check product_id and product_price is number
            if product_id.isnumeric() and product_price.isnumeric():

                # cur.execute("SELECT product_id FROM products ")
                # check_id_duplicate = cur.fetchall()
                # print(check_id_duplicate)

                cur.execute("INSERT INTO products (product_id, product_name, product_price) VALUES (%s, %s,%s)",
                            (product_id, product_name, product_price))
                db.connection.commit()
                # print("Product added successfully")
                flash("success add product")
                client.publish("price_tag1", payload= json_data, qos=1)
                return redirect(url_for('products'))
            

            else:
                flash("id and price must be number")
                # print("Product id and price must be number")

        except Exception as e:
            print(e)
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
                client.publish("price_tag1", payload="success add product", qos=1)
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
    cur.execute("DELETE FROM products WHERE id = %s", (id,))
    db.connection.commit()
    client.publish("price_tag1", payload="delete product", qos=1)
    return redirect(url_for('products'))


@app.route('/devices')
def devices():
    devices = MD.get_all_devices(db)
    product_id = MP.get_product_id(db)
    return render_template('device.html', devices=devices, product_id=product_id)


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

                cur.execute(
                    "INSERT INTO devices (chipID, name, status) VALUES (%s, %s,%s)", (chipID, name, 0))
                db.connection.commit()

                flash("success add device")
                return redirect(url_for('devices'))

        except Exception as e:
            flash("error")
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
            product_id = request.form['product_id']
            # print(product_id)
            cur = db.connection.cursor()

            # check product_id and product_price is number
            if device_id.isnumeric():

                sql = "UPDATE devices SET chipID = %s, name = %s, product_id = %s WHERE id = %s"
                val = (device_id, device_name, product_id, id)

                cur.execute(sql, val)

                db.connection.commit()
                flash("success update")
                return redirect(url_for('devices'))

        except Exception as e:
            flash("error :")
            raise e

        finally:
            return redirect(url_for('devices'))


@app.route('/delete_device/<id>', methods=['GET'])
@login_required
def delete_device(id):

    cur = db.connection.cursor()
    cur.execute("DELETE FROM devices WHERE id = %s", (id,))
    db.connection.commit()
    return redirect(url_for('devices'))


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.run()
