from .entities.Device import Device


class ModelDevice():

    @classmethod
    def get_all_devices(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT * FROM devices"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            devices = []
            for row in rows:
                device = Device(row[0], row[1], row[2], row[3], row[4])
                devices.append(device)
            return devices
        except Exception as e:
            raise Exception(e)

    @classmethod
    def addDevice(self, db, chipID, name, status, last_seen):
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                "INSERT INTO devices (chipID, name, status, last_seen) VALUES (%s, %s,%s,%s)", (chipID, name, status,last_seen))
            db.connection.commit()
            return "Device added successfully"
        except Exception as e:
            raise Exception(e)

    @classmethod
    def count_device(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT COUNT(id) FROM devices"""
            cursor.execute(sql)
            count = cursor.fetchone()
            for i in count:
                count = i

            return count
        except Exception as e:
            raise Exception(e)

    @classmethod
    def statusON_device(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT COUNT(id) FROM devices WHERE status = 1"""
            cursor.execute(sql)
            on_status = cursor.fetchone()
            for i in on_status:
                on_status = i
            return on_status
        except Exception as e:
            raise Exception(e)

    @classmethod
    def statusOFF_device(self, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT COUNT(id) FROM devices WHERE status = 0"""
            cursor.execute(sql)
            off_status = cursor.fetchone()
            for i in off_status:
                off_status = i
            return off_status
        except Exception as e:
            raise Exception(e)

    @classmethod
    def getDeviceBychipID(self, db, chipID):
        try:
            cursor = db.connection.cursor()
            
            cursor.execute("SELECT chipID FROM devices WHERE chipID = %s", (chipID,) )
            chipID = cursor.fetchone()
            
            if chipID is None:
                return False
            else:
                return True
        except Exception as e:
            raise Exception(e)
        
    @classmethod
    def updateDevice(self, db, chipID, status,last_seen):
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                "UPDATE devices SET status = %s ,last_seen = %s WHERE chipID = %s", (status,last_seen, chipID))
            db.connection.commit()
            return "Device updated successfully"
        except Exception as e:
            raise Exception(e)
        
    @classmethod
    def checkHasProduct(self, db, chipID):
        try:
            cursor = db.connection.cursor()
            cursor.execute("SELECT product_id FROM devices WHERE chipID = %s", (chipID,) )
            product_id = cursor.fetchone()
            if chipID is None:
                return False
            else:
                return product_id
        except Exception as e:
            raise Exception(e)