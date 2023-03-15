from sqlite3 import IntegrityError
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mqtt import Mqtt
from datetime import datetime

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

# config database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/testpythondeploy777'
app.config['MYSQL_HOST'] = config['development'].MYSQL_HOST
app.config['MYSQL_USER'] = config['development'].MYSQL_USER
app.config['MYSQL_PASSWORD'] = config['development'].MYSQL_PASSWORD
app.config['MYSQL_DB'] = config['development'].MYSQL_DB


mqtt_client = Mqtt(app)
db = MySQL(app)
csrf = CSRFProtect(app)


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        # mqtt_client.subscribe(topic)  # subscribe topic
        mqtt_client.subscribe("test/device/price")  # subscribe topic2
        # mqtt_client.subscribe("/pricetagProjectNPU/test/devices")  # subscribe topic2

    else:
        print('Bad connection. Code:', rc)

mqtt_msg = ""

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    with app.app_context():
        
        try:
            mqtt_msg = message.payload.decode()
            json_data = json.loads(mqtt_msg)  
            mode = json_data['mode']
            # timestamp = json_data['timestamp']
            # msg = json_data['msg']
            chipID = json_data['chip_id']
            time2 = json_data['time2']
            id = json_data['id']
            print(json_data)
            
    
            cur = db.connection.cursor()

            if str(mode) == "ACT":
                try:
                    # update time2 to database
                    sql = "UPDATE test SET time2 = %s WHERE id = %s"
                    val = (time2, id)
                    cur.execute(sql, val)
                    db.connection.commit()
                    print ("Updated test successfully")
                except IntegrityError as e:
                    raise e
                except Exception as e:
                    raise e
        except Exception as e:
            raise Exception(e)
        
i = 1
topic = "/pricetagProjectNPU/test/devices"


@app.route('/publish_mqtt')
def publish_mqtt():
    global i
    print(i)
    with app.app_context():
        
        
        datetime_object = datetime.now()
        time1 = datetime_object.strftime("%H:%M:%S") 
        # mqtt_client.publish(topic, i)
        json_data = {
            "mode": "single",
            "id":i,
            "chip_id":123456789,
            "msg":["name",8],
            "timestamp":time1
        }
        mqtt_client.publish(topic, json.dumps(json_data))
        
        cur = db.connection.cursor()
        
        # commit to database
        sql = "INSERT INTO test (id, name, time1) VALUES (%s, %s,%s)"
        val = (i, "test", time1)
        cur.execute(sql, val)
        db.connection.commit()
        
        print(json.dumps(json_data))
        
        i = i + 1
        
        
        
        
        return "SYN to esp32"
        

        

if __name__ == '__main__':
    
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.run()