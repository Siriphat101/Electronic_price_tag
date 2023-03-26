
from sqlite3 import IntegrityError

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mqtt import Mqtt
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import json
# MQTT library
import time
import calendar

from config import config

# models
from models.ModelUser import ModelUser
from models.ModelProduct import ModelProduct as MP
from models.ModelDevice import ModelDevice as MD
from models.ModelItem import ModelItem as MI

# entities
from models.entities.User import User

app = Flask(__name__)

# config MQTT
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
# Set this item when you need to verify username and password
app.config['MQTT_USERNAME'] = ''
# Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
# If your broker supports TLS, set it True
app.config['MQTT_TLS_ENABLED'] = False
topic = '/pricetagProjectNPU'
topic2 = 'serial2/data'

# config database
app.config['MYSQL_HOST'] = config['development'].MYSQL_HOST
app.config['MYSQL_USER'] = config['development'].MYSQL_USER
app.config['MYSQL_PASSWORD'] = config['development'].MYSQL_PASSWORD
app.config['MYSQL_DB'] = config['development'].MYSQL_DB

mqtt_client = Mqtt(app)
db = MySQL(app)

csrf = CSRFProtect(app)
login_manager = LoginManager(app)

scheduler = BackgroundScheduler()

def check_device_status():
    with app.app_context():
        try:
            cur = db.connection.cursor()
            cur.execute("SELECT chipID, last_seen FROM devices")
            devices = cur.fetchall()
            for device in devices:
                chipID = device[0]
                last_seen = device[1]
                print("chipID: ", chipID)
                if last_seen is None:
                    # device hasn't connected yet
                    print("last_seen: is none", last_seen)
                    status = 0
                else:
                    print("last_seen else: ", last_seen)
                    
                    now = datetime.datetime.now()
                    delta = now - last_seen
                    print("delta: ", delta)
                    print("delta.seconds: ", delta.seconds)
                    if delta.seconds > 60:
                        status = 0
                    else:
                        status = 1
                cur.execute("UPDATE devices SET status = %s WHERE chipID = %s", (status, chipID))

            db.connection.commit()
        except Exception as e:
            raise Exception(e)
        finally:
            return True

scheduler.add_job(check_device_status, 'interval', minutes=1)
scheduler.start()

@login_manager.user_loader
def load_user(user_id):
    return ModelUser.get_by_id(db, user_id)


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic)  
        mqtt_client.subscribe(topic2)  

    else:
        print('Bad connection. Code:', rc)


mqtt_msg = ""
@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    with app.app_context():
        try:
            mqtt_msg = message.payload.decode()
            json_data = json.loads(mqtt_msg)  
            
            msg = json_data['msg']
            chipID = json_data['chipID']
            status = json_data['status']
            
            last_seen = datetime.datetime.now()
            last_seen = last_seen.strftime("%Y-%m-%d %H:%M:%S.%f")
            
            msg_str = str(msg)
            name = "node" + str(chipID)
            
            current_GMT = time.gmtime()
            ts = calendar.timegm(current_GMT)
            # StrTimeStamp = str(ts)
    
            cur = db.connection.cursor()

            if msg_str == "Device":
                try:
                    check = MD.getDeviceBychipID(db, chipID)
                    print(check)
                    if check is False:
                        # print("Device not found")
                        # add device
                        # print("last_seen: ", last_seen)
                        MD.addDevice(db, chipID, name, status, last_seen)
                    else:
                        # print("Device found")
                        # update device
                        
                        if status == 1:
                            # print("Device is ON")
                            # print("last_seen: ", last_seen)
                            
                            MD.updateDevice(db, chipID, status, last_seen)
         
                except IntegrityError as e:
                    raise e
                except Exception as e:
                    raise e
                
            elif(msg_str=="ACT"):
                try:
                    print("act:",last_seen)
                    mqtt_client.publish("turnarountime", json.dumps({"msg": "ACK", "chipID": chipID, "status": status, "last_seen": last_seen}), qos=1)
                    
                    
                except Exception as e:
                    raise Exception(e)
                
        except Exception as e:
            raise Exception(e)
        finally:
            return True


@app.route('/')
def home():
    

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


@app.route('/products')
@login_required
def products():
    products = MP.get_all_products(db)
    return render_template('product.html', products=products)


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

                cur.execute("INSERT INTO products (product_id, product_name, product_price) VALUES (%s, %s,%s)",
                            (product_id, product_name, product_price))
                db.connection.commit()
                # print("Product added successfully")
                flash("success add product")

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
                # timestamp
                # Current GMT time in a tuple format
                current_GMT = time.gmtime()
                ts = calendar.timegm(current_GMT)
                StrTimeStamp = str(ts)

                sql = "UPDATE products SET product_id = %s, product_name = %s, product_price = %s WHERE id = %s"
                val = (product_id, product_name, product_price, id)

                cur.execute(sql, val)

                db.connection.commit()
                flash("success update")

                # mqtt publish//
                sql = """SELECT  chipID FROM devices WHERE product_id = '{}'""".format(
                    product_id)
                cur.execute(sql)
                row = cur.fetchall()
                devices = []
                for row in row:
                    devices.append(row[0])
                print(devices)
                for device in devices:
                    data_json = {
                        "mode": "single",
                        "chip_id": device,
                        "msg": [
                            product_name, product_price,

                        ],
                        "timestamp": ts
                    }

                    mqtt_client.publish("/pricetagProjectNPU",
                                        json.dumps(data_json), qos=1)
               
                return redirect(url_for('products'))

            else:
                flash("id and price must be number")
        except Exception as e:
            raise e

        finally:

            return redirect(url_for('products'))


@app.route('/delete_product/<id>', methods=['GET'])
@login_required
def delete_product(id):

    cur = db.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", (id,))
    db.connection.commit()
    # client.publish("price_tag1", payload="delete product", qos=1)
    # if delete product is successful
    # send data to esp32. esp32 show message logo project
    mqtt_client.publish("/pricetagProjectNPU", "delete product", qos=1)
    return redirect(url_for('products'))


@app.route('/devices')
def devices():
    devices = MD.get_all_devices(db)
    product_id = MP.get_product_id(db)
    return render_template('device.html', devices=devices, product_id=product_id)


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
            print(e)
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
            
            

            cur = db.connection.cursor()

            # check device_id
            if device_id.isnumeric():

                sql = "UPDATE devices SET chipID = %s, name = %s, product_id = %s WHERE id = %s"
                val = (device_id, device_name, product_id, id)

                cur.execute(sql, val)

                db.connection.commit()

                flash("success update")

                current_GMT = time.gmtime()
                ts = calendar.timegm(current_GMT)
                StrTimeStamp = str(ts)
                last_seen = datetime.datetime.now()
                last_seen = last_seen.strftime("%Y-%m-%d %H:%M:%S.%f")
                sql = """SELECT  product_name, product_price FROM products WHERE product_id = '{}'""".format(
                    product_id)
                cur.execute(sql)
                row = cur.fetchone()
                print(row)
                data_json = {
                    "mode": "single",
                    "chip_id": device_id,
                    "msg": [
                        row[0], row[1]
                    ],
                    "timestamp": last_seen
                }

                # client.publish("price_tag1", payload= json.dumps(data_json), qos=1)
                mqtt_client.publish("/pricetagProjectNPU",json.dumps(data_json), qos=1)
                mqtt_client.publish("turnarountime",json.dumps(data_json), qos=1)
                

                return redirect(url_for('devices'))

        except Exception as e:
            print(e)
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

@app.errorhandler(401)
def page_not_found(e):
    return render_template("login.html")


@app.errorhandler(404)
def page_not_found(e):
    return "404"

@app.errorhandler(500)
def page_not_found505(e):
    return "500"

if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    
    app.run()